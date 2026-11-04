"""network_access.py — сетевой расчёт пешеходной доступности (IduEdu 2.2 + ObjectNat 2.1).

Окружение: .venv-objectnat (ObjectNat 2.1.0, iduedu[io] 2.2.0) — отдельное от основного
пайплайна, по методологии курса (см. pskov-blocksnet/docs/libraries/*.md).

Расчёт:
  1. пешеходный граф по территории v3 (get_walk_graph, Overpass);
  2. зоны покрытия сервисов по сети: школы 500 м, детсады 300 м, здоровье 500 м, аптеки 300 м
     (get_graph_coverage, weight_type="length_meter");
  3. изохроны пешеходной доступности метро 400/800 м (get_graph_isochrones);
  4. доля жилых зданий (по центроидам) внутри зон.

Выход: data/processed/{coverage_*,isochrones_metro}.geojson, data/processed/network_access.json.
Запуск: .venv-objectnat/bin/python scripts/network_access.py
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from iduedu import get_walk_graph
from objectnat import get_graph_coverage, get_graph_isochrones

R = Path(__file__).resolve().parents[1]
PROC = R / "data/processed"
CRS_M = 32636

LIVING = ["apartments", "residential", "dormitory", "detached", "house", "semidetached_house", "yes"]


def rep_points(gdf):
    """Представительные точки для смешанной геометрии (Point остаются, полигоны — representative_point)."""
    g = gdf.geometry
    pts = gdf.copy()
    poly = g.geom_type.isin(["Polygon", "MultiPolygon"])
    pts.loc[poly, "geometry"] = g[poly].to_crs(CRS_M).representative_point().to_crs(4326)
    return pts


def main():
    versions = gpd.read_file(PROC / "boundary_versions.geojson").set_index("version")
    v3 = versions.loc["v3", "geometry"]
    building = gpd.read_file(PROC / "building.geojson")
    living = building[building.building.isin(LIVING) & building.within(v3)]
    living_pts = living.to_crs(CRS_M).geometry.centroid.to_crs(4326)
    print(f"жилых зданий в v3: {len(living)}")

    graph_cache = PROC / "walk_graph.urbangraph"
    if graph_cache.exists():
        from iduedu import read_urban_graph
        g_walk = read_urban_graph(graph_cache)
        print("граф из кэша:", graph_cache.name)
    else:
        print("строим пешеходный граф по территории v3 (Overpass)...")
        g_walk = get_walk_graph(territory=v3, keep_largest_subgraph=True)
        g_walk.validate()
        try:
            from iduedu import write_urban_graph
            write_urban_graph(g_walk, graph_cache)
            print("кэш графа:", graph_cache.name)
        except Exception as e:  # noqa: BLE001
            print("кэш графа не записан:", e)

    services = gpd.read_file(PROC / "services.geojson")
    stations = gpd.read_file(PROC / "stations.geojson")

    groups = {  # (фильтр amenity, cutoff м)
        "schools": ("school", 500),
        "kindergartens": ("kindergarten", 300),
        "health": (["clinic", "doctors", "hospital"], 500),
        "pharmacies": (["pharmacy"], 300),
    }

    results = {"living_total": int(len(living))}
    for name, (flt, cutoff) in groups.items():
        svc = services[services.amenity.isin(flt if isinstance(flt, list) else [flt])]
        svc_pts = rep_points(svc)
        cov = get_graph_coverage(g_walk, gdf_destinations=svc_pts, weight_type="length_meter",
                                 weight_value_cutoff=cutoff, geometry_type="radius")
        cov_path = PROC / f"coverage_{name}.geojson"
        cov.to_file(cov_path, driver="GeoJSON")
        zone = cov.union_all()
        share = 100 * living_pts.within(zone).mean()
        results[f"{name}_cutoff_m"] = cutoff
        results[f"{name}_objects"] = int(len(svc))
        results[f"{name}_share"] = round(float(share), 1)
        print(f"{name}: сервисов {len(svc)}, сетевой охват {share:.1f} % жилых зданий ({cutoff} м) -> {cov_path.name}")

    st_pts = rep_points(stations)
    iso = get_graph_isochrones(g_walk, weight_value_cutoff=800, gdf_origins=st_pts,
                               weight_type="length_meter", geometry_type="radius")
    iso.to_file(PROC / "isochrones_metro.geojson", driver="GeoJSON")
    if "weight_value" in iso.columns:
        z400 = iso[iso.weight_value <= 400].union_all()
        z800 = iso[iso.weight_value <= 800].union_all()
    else:
        z400, z800 = iso.union_all(), iso.union_all()
    results["metro_400_share"] = round(float(100 * living_pts.within(z400).mean()), 1)
    results["metro_800_share"] = round(float(100 * living_pts.within(z800).mean()), 1)
    print(f"метро: 400 м — {results['metro_400_share']} %, 800 м — {results['metro_800_share']} % жилых зданий")

    (PROC / "network_access.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print("итоги:", json.dumps(results, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
