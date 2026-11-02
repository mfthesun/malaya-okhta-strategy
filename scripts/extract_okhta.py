"""extract_okhta.py — выгрузка слоёв Малой Охты из PBF-выписки СЗФО (pyosmium, без Overpass).

pyrosm с bounding_box теряет объекты на чанках (проверено 02.11.2026: 2 780 зданий в bbox
вместо ~20 тыс.), поэтому выгружаем сами: FileProcessor с with_locations по bbox с нужными тегами.

Выход: data/processed/{building,roads,green,water,services,stations}.geojson
Запуск: .venv/bin/python scripts/extract_okhta.py
"""
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import osmium
import shapely
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import linemerge, polygonize

R = Path(__file__).resolve().parents[1]
RAW, PROC = R / "data/raw", R / "data/processed"
PBF = RAW / "nwfd-latest.osm.pbf"

# bbox v3 + запас ~250 м (из ноутбука 01)
LON_MIN, LAT_MIN, LON_MAX, LAT_MAX = 30.3891, 59.9102, 30.4538, 59.9657

BUILDING_KEYS = {"building"}
HIGHWAY = {"motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential",
           "living_street", "pedestrian", "footway", "cycleway", "service", "motorway_link",
           "trunk_link", "primary_link", "secondary_link", "tertiary_link", "track", "path", "steps"}
LANDUSE = {"forest", "grass", "meadow", "recreation_ground", "cemetery", "allotments", "industrial",
           "residential", "retail", "commercial", "construction", "garages"}
LEISURE = {"park", "garden", "pitch", "playground", "sports_centre", "stadium", "water_park", "track"}
NATURAL = {"water", "wood", "scrub", "grassland", "park", "beach", "wetland", "sand"}
WATERWAY = {"riverbank", "dock", "canal", "river", "stream"}
AMENITY = {"school", "kindergarten", "college", "university", "library", "clinic", "doctors", "hospital",
           "pharmacy", "community_centre", "police", "fire_station", "place_of_worship", "bank",
           "post_office", "cinema", "theatre", "arts_centre", "social_facility"}
RAILWAY = {"station", "halt"}
SUBWAY = {"subway"}
RIVERS_WANTED = {"Нева", "Охта"}  # мультиполигоны только этих рек; прочая вода берётся ways-ами


def in_bbox(lon, lat):
    return LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX


def way_in_bbox(locs):
    return any(in_bbox(p.lon, p.lat) for p in locs)


def to_gdf(rows, cols):
    df = pd.DataFrame(rows, columns=cols)
    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")


def main():
    if not PBF.exists():
        print("PBF не найден:", PBF)
        return 1
    PROC.mkdir(exist_ok=True)

    bld, roads, green, water, svc, st = [], [], [], [], [], []
    rels = {}  # rel_id -> (name, [way_ids])

    print("проход 1: ways, узлы, relations рек (FileProcessor + locations)...")
    for obj in osmium.FileProcessor(str(PBF)).with_locations():
        kind = obj.type_str()  # 'n' | 'w' | 'r'
        if kind == "n":
            if not in_bbox(obj.location.lon, obj.location.lat):
                continue
            tags = obj.tags
            if tags.get("amenity") in AMENITY:
                svc.append((obj.id, tags.get("amenity"), tags.get("name", ""),
                            Point(obj.location.lon, obj.location.lat)))
            if tags.get("railway") in RAILWAY or tags.get("station") in SUBWAY:
                st.append((obj.id, tags.get("railway", ""), tags.get("station", ""), tags.get("name", ""),
                           Point(obj.location.lon, obj.location.lat)))
            continue
        if kind == "r":
            tags = obj.tags
            if tags.get("type") == "multipolygon" and tags.get("name", "") in RIVERS_WANTED:
                ids = [m.ref for m in obj.members if m.type == "w"]
                rels[obj.id] = (tags.get("name", ""), ids)
            continue
        # way
        tags = obj.tags
        pts = [(n.location.lon, n.location.lat) for n in obj.nodes]
        if not pts or not any(in_bbox(x, y) for x, y in pts):
            continue
        gid = obj.id
        if "building" in tags:
            if len(pts) >= 4 and pts[0] == pts[-1]:
                bld.append((gid, tags.get("building", "yes"), tags.get("name", ""),
                            tags.get("building:levels", ""), tags.get("start_date", ""), Polygon(pts)))
        elif tags.get("highway") in HIGHWAY:
            roads.append((gid, tags.get("highway"), tags.get("name", ""), tags.get("maxspeed", ""),
                          tags.get("lanes", ""), LineString(pts)))
        if tags.get("landuse") in LANDUSE or tags.get("leisure") in LEISURE or tags.get("natural") in NATURAL:
            if len(pts) >= 4 and pts[0] == pts[-1]:
                val = tags.get("landuse") or tags.get("leisure") or tags.get("natural")
                green.append((gid, val, tags.get("name", ""), Polygon(pts)))
        if tags.get("natural") == "water" or tags.get("waterway") in WATERWAY:
            if len(pts) >= 4 and pts[0] == pts[-1]:
                water.append((gid, tags.get("natural", ""), tags.get("waterway", ""), tags.get("name", ""),
                              Polygon(pts)))
        # сервисы тегируются и на полигонах-участках (школы, детсады, клиники) — берём их тоже
        if tags.get("amenity") in AMENITY:
            if len(pts) >= 4 and pts[0] == pts[-1]:
                svc.append((gid, tags.get("amenity"), tags.get("name", ""), Polygon(pts)))

    print(f"  зданий {len(bld)}, дорог {len(roads)}, зелени {len(green)}, "
          f"воды(ways) {len(water)}, сервисов {len(svc)}, станций {len(st)}")
    print("  мультиполигонов рек:", len(rels))

    rel_polys = []
    if rels:
        wanted = {wid for _, ids in rels.values() for wid in ids}
        print(f"проход 2: {len(wanted)} member-ways рек...")
        geoms = {}
        for obj in osmium.FileProcessor(str(PBF)).with_locations():
            if obj.type_str() == "w" and obj.id in wanted:
                geoms[obj.id] = [(n.location.lon, n.location.lat) for n in obj.nodes]
        for rid, (name, ids) in rels.items():
            lines = [LineString(geoms[wid]) for wid in ids if wid in geoms and len(geoms[wid]) >= 2]
            if len(lines) < 2:
                continue
            merged = linemerge(lines)
            polys = list(polygonize(merged))
            if polys:
                rel_polys.append((rid, "water", "multipolygon", name, shapely.union_all(polys)))
    print("  полигонов из мультиполигонов:", len(rel_polys))

    bld_g = to_gdf(bld, ["osm_id", "building", "name", "floors", "start_date", "geometry"])
    bld_g["floors"] = pd.to_numeric(bld_g["floors"], errors="coerce")
    bld_g.to_file(PROC / "building.geojson", driver="GeoJSON")
    to_gdf(roads, ["osm_id", "highway", "name", "maxspeed", "lanes", "geometry"]).to_file(
        PROC / "roads.geojson", driver="GeoJSON")
    to_gdf(green, ["osm_id", "kind", "name", "geometry"]).to_file(
        PROC / "green.geojson", driver="GeoJSON")
    wat = to_gdf(water, ["osm_id", "natural", "waterway", "name", "geometry"])
    if rel_polys:
        wat = pd.concat([wat, to_gdf(rel_polys, ["osm_id", "natural", "waterway", "name", "geometry"])],
                        ignore_index=True)
    wat.to_file(PROC / "water.geojson", driver="GeoJSON")
    to_gdf(svc, ["osm_id", "amenity", "name", "geometry"]).to_file(
        PROC / "services.geojson", driver="GeoJSON")
    to_gdf(st, ["osm_id", "railway", "station", "name", "geometry"]).to_file(
        PROC / "stations.geojson", driver="GeoJSON")

    print("\nитоги:")
    print(f"  building: {len(bld_g)}")
    print(f"  roads: {len(roads)}")
    print(f"  green: {len(green)}")
    print(f"  water: {len(wat)} (полигоны)")
    print(f"  services: {len(svc)}")
    print(f"  stations: {len(st)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
