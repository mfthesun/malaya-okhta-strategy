"""network_access_fallback.py — сетевой расчёт доступности локально, без Overpass.

Пешеходный граф строится из data/processed/roads.geojson (линии OSM, уже скачаны):
узлы — концы сегментов, рёбра — length_meter (пешеходная скорость 5 км/ч = 83,3 м/мин).
Пешеходные типы сети: footway, path, steps, pedestrian, living_street, residential,
service, unclassified, tertiary(+link), secondary(+link), primary(+link), track.
Считается та же статистика, что и scripts/network_access.py (IduEdu/ObjectNat):
доля жилых зданий в сетевом пороге от сервисов + от метро.

Выход: data/processed/network_access.json, data/processed/coverage_*.geojson (зоны достижимости),
       data/processed/isochrones_metro.geojson.
Запуск: .venv/bin/python scripts/network_access_fallback.py
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely.geometry import Point
from shapely.strtree import STRtree

R = Path(__file__).resolve().parents[1]
PROC = R / "data/processed"
CRS_M = 32636
WALK_SPEED = 83.3333  # м/мин (5 км/ч) — как в IduEdu

WALKABLE = {"footway", "path", "steps", "pedestrian", "living_street", "residential", "service",
            "unclassified", "tertiary", "tertiary_link", "secondary", "secondary_link",
            "primary", "primary_link", "track"}

LIVING = ["apartments", "residential", "dormitory", "detached", "house", "semidetached_house", "yes"]


def build_graph(roads):
    """Пешеходный граф networkx из линий дорог (в UTM 36N, метры)."""
    g = nx.Graph()
    coords, ids = {}, {}
    road = roads[roads.highway.isin(WALKABLE)]
    for geom in road.to_crs(CRS_M).geometry:
        lines = geom.geoms if geom.geom_type == "MultiLineString" else [geom]
        for line in lines:
            pts = list(line.coords)
            for a, b in zip(pts[:-1], pts[1:]):
                for c in (a, b):
                    if c not in coords:
                        nid = len(coords)
                        coords[c] = nid
                        ids[nid] = c
                d = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
                if d > 0.5:
                    g.add_edge(coords[a], coords[b], length_meter=d)
    nx.set_edge_attributes(g, {e: w["length_meter"] / WALK_SPEED for e, w in g.edges.items()}, "time_min")
    nodes = gpd.GeoDataFrame(
        {"node_id": list(ids.keys())},
        geometry=[Point(ids[i]) for i in ids], crs=f"EPSG:{CRS_M}")
    return g, nodes


def attach(points_gdf, nodes):
    """Привязка точек к ближайшим узлам графа (STRtree.nearest)."""
    tree = STRtree(nodes.geometry.values)
    nearest = tree.nearest(points_gdf.geometry.values)  # индекс в дереве для каждой точки
    return [int(nodes.iloc[j].node_id) for j in nearest]


def reachable_shares(graph, nodes, svc_pts, cutoff_m, living_attach):
    """Доля жилых зданий в сетевом пороге cutoff_m от хотя бы одного сервиса.

    Мультиисточниковая Dijkstra от узлов сервисов (weight = length_meter);
    к сетевой дистанции добавляется пешеходный подход здания до узла сети.
    """
    svc = rep_points(svc_pts)
    svc_nodes = attach(svc, nodes)
    dist = nx.multi_source_dijkstra_path_length(graph, set(svc_nodes), cutoff=cutoff_m,
                                                weight="length_meter")
    ok = sum(1 for node_id, approach in living_attach if dist.get(node_id, 1e18) + approach <= cutoff_m)
    # зона достижимости для карты: коридоры сети в пороге
    zone = nodes[nodes.node_id.isin(dist.keys())].geometry.union_all().buffer(15)
    return 100 * ok / len(living_attach), zone


def rep_points(gdf):
    """Представительные точки в метрической CRS (полигоны — representative_point, точки — сами)."""
    pts = gdf.to_crs(CRS_M).copy()
    poly = pts.geometry.geom_type.isin(["Polygon", "MultiPolygon"])
    pts.loc[poly, "geometry"] = pts.geometry[poly].representative_point()
    return pts


def main():
    versions = gpd.read_file(PROC / "boundary_versions.geojson").set_index("version")
    v3 = versions.loc["v3", "geometry"]
    building = gpd.read_file(PROC / "building.geojson")
    living = building[building.building.isin(LIVING) & building.within(v3)]
    living_pts = living.to_crs(CRS_M).geometry.centroid
    print(f"жилых зданий в v3: {len(living)}")

    roads = gpd.read_file(PROC / "roads.geojson")
    graph, nodes = build_graph(roads)
    print(f"граф: {graph.number_of_nodes()} узлов, {graph.number_of_edges()} рёбер")
    # привязка жилых зданий: узел + длина пешеходного подхода до сети
    tree = STRtree(nodes.geometry.values)
    nearest = tree.nearest(living_pts.values)
    living_attach = []
    for i, j in enumerate(nearest):
        d0 = living_pts.iloc[i].distance(nodes.geometry.iloc[j])
        living_attach.append((int(nodes.iloc[j].node_id), float(d0)))

    services = gpd.read_file(PROC / "services.geojson")
    stations = gpd.read_file(PROC / "stations.geojson")

    results = {"living_total": int(len(living)), "method": "networkx из roads.geojson (UTM 36N)"}
    groups = {
        "schools": (["school"], 500),
        "kindergartens": (["kindergarten"], 300),
        "health": (["clinic", "doctors", "hospital"], 500),
        "pharmacies": (["pharmacy"], 300),
    }
    for name, (flt, cutoff) in groups.items():
        svc = services[services.amenity.isin(flt)]
        share, zone = reachable_shares(graph, nodes, svc, cutoff, living_attach)
        gpd.GeoSeries([zone], crs=f"EPSG:{CRS_M}").to_crs(4326).to_file(
            PROC / f"coverage_{name}.geojson", driver="GeoJSON")
        results[f"{name}_cutoff_m"] = cutoff
        results[f"{name}_objects"] = int(len(svc))
        results[f"{name}_share"] = round(float(share), 1)
        print(f"{name}: сервисов {len(svc)}, сетевой охват {share:.1f} % ({cutoff} м)")

    st = stations
    for cutoff in (400, 800):
        share, zone = reachable_shares(graph, nodes, st, cutoff, living_attach)
        results[f"metro_{cutoff}_share"] = round(float(share), 1)
        gpd.GeoSeries([zone], crs=f"EPSG:{CRS_M}").to_crs(4326).to_file(
            PROC / f"isochrones_metro_{cutoff}.geojson", driver="GeoJSON")
        print(f"метро {cutoff} м: {share:.1f} % жилых зданий")

    (PROC / "network_access.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print("итоги:", json.dumps(results, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
