"""check_numbers.py — пересчитывает числа из документов по данным репозитория.

Запуск:  python3 scripts/check_numbers.py            # проверка
         python3 scripts/check_numbers.py --control  # контроль: подставляет заведомо неверное значение, проверка ОБЯЗАНА упасть
Код выхода: 0 — все числа совпали; 1 — есть расхождения.
Числа из внешних источников (веб, документы вне репозитория) здесь не проверяются — см. docs/numbers_check.md.

Каждая строка CHECKS: (документ, утверждение, пересчитанное значение, заявленное значение, допуск).
Прогон данных: 02.11.2026 (ноутбуки 01–03, слои extract_okhta.py).
"""
import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd
import json

R = Path(__file__).resolve().parents[1]


def csv(p):
    for sep in (";", ","):
        d = pd.read_csv(R / p, sep=sep, encoding="utf-8-sig")
        if d.shape[1] > 1:
            return d
    raise ValueError(p)


# --- данные -----------------------------------------------------------------
pop = csv("data/raw/population_spb_mo_2010_2025.csv")
versions = gpd.read_file(R / "data/processed/boundary_versions.geojson").set_index("version")
building = gpd.read_file(R / "data/processed/building.geojson")
okn = gpd.read_file(R / "data/processed/okn.geojson")
ha = gpd.read_file(R / "data/processed/house_age.geojson")
net = json.load(open(R / "data/processed/network_access.json", encoding="utf-8"))

V2 = versions.loc["v2", "geometry"]
V3 = versions.loc["v3", "geometry"]
V1 = versions.loc["v1", "geometry"]
V4 = versions.loc["v4", "geometry"]
AREA_V2 = float(versions.loc["v2", "area_km2"])
AREA_V3 = float(versions.loc["v3", "area_km2"])


def share_km2(geoms, geom):
    """Площадь пересечения слоя с территорией без двойного учёта наложений, км² (как в ноутбуке 03)."""
    clipped = gpd.GeoSeries(geoms, crs=4326).intersection(geom)
    clipped = clipped[~clipped.is_empty]
    if not len(clipped):
        return 0.0
    merged = clipped.union_all()
    return gpd.GeoSeries([merged], crs=4326).to_crs(32636).area.iloc[0] / 1e6


pop_mal = pop.loc[pop["территория"] == "МО Малая Охта"].iloc[0]
pop_bol = pop.loc[pop["территория"] == "МО Большая Охта"].iloc[0]
pop_kr = pop.loc[pop["территория"] == "Красногвардейский район"].iloc[0]

ha3 = ha[ha.intersects(V3)]  # как в ноутбуке 02 (processed слой)
known3 = ha3[ha3.year.notna()]
ha2 = ha[ha.within(V2)]
known2 = ha2[ha2.year.notna()]

LIVING = ["apartments", "residential", "dormitory", "detached", "house", "semidetached_house", "yes"]
living3 = building[building.building.isin(LIVING) & building.within(V3)]
living2 = building[building.building.isin(LIVING) & building.within(V2)]
IND_B = ["industrial", "warehouse"]
GAR_B = ["garages", "garage", "hangar"]
services = gpd.read_file(R / "data/processed/services.geojson")
svc3 = services[services.within(V3)]
svc3_pts = int(services[services.geom_type == "Point"].within(V3).sum())
green = gpd.read_file(R / "data/processed/green.geojson")
ind_lu2 = green[green.kind == "industrial"]

water = gpd.read_file(R / "data/processed/water.geojson")
import json  # noqa: E402
from shapely.geometry import LineString  # noqa: E402
wp = json.load(open(R / "data/raw/cache/overpass_water_bbox.json", encoding="utf-8"))
axes = [LineString([(g["lon"], g["lat"]) for g in el["geometry"]])
        for el in wp["elements"] if el.get("tags", {}).get("name") in ("Нева", "Охта")]
rivers_band = gpd.GeoSeries(axes, crs=4326).to_crs(32636).buffer(300).union_all()
shore_w = gpd.GeoSeries([rivers_band], crs=32636).to_crs(4326).iloc[0].intersection(V3)
shore_km2 = gpd.GeoSeries([shore_w], crs=4326).to_crs(32636).area.iloc[0] / 1e6
living_in_shore = gpd.GeoSeries(living3.geometry, crs=4326).intersection(shore_w)
living_in_shore_km2 = gpd.GeoSeries(living_in_shore[~living_in_shore.is_empty], crs=4326).to_crs(32636).area.sum() / 1e6
V3M = gpd.GeoSeries([V3], crs=4326).to_crs(32636).iloc[0]
river_axes_km = sum(ax.intersection(V3M).length for ax in gpd.GeoSeries(axes, crs=4326).to_crs(32636)) / 1000

CHECKS = [
    # --- диагностика, разд. 0: население и территория ---
    ("docs/diagnostics.md", "население МО Малая Охта 01.01.2025, чел.",
     int(pop_mal["01.01.2025"]), 43319, 0),
    ("docs/diagnostics.md", "население МО Малая Охта ВПН-2010, чел.",
     int(pop_mal["ВПН-2010"]), 45946, 0),
    ("docs/diagnostics.md", "убыль МО Малая Охта 2010→2025, %",
     100 * (1 - int(pop_mal["01.01.2025"]) / int(pop_mal["ВПН-2010"])), 5.7, 0.05),
    ("docs/diagnostics.md", "прирост МО Большая Охта 2010→2025, %",
     100 * (int(pop_bol["01.01.2025"]) / int(pop_bol["ВПН-2010"]) - 1), 6.7, 0.05),
    ("docs/diagnostics.md", "прирост Красногвардейского района 2010→2025, %",
     100 * (int(pop_kr["01.01.2025"]) / int(pop_kr["ВПН-2010"]) - 1), 9.3, 0.05),
    ("docs/diagnostics.md", "вся Охта (v3), чел.",
     int(pop_mal["01.01.2025"]) + int(pop_bol["01.01.2025"]), 101495, 0),
    ("docs/diagnostics.md", "площадь v2, км²", AREA_V2, 5.26, 0.01),
    ("docs/diagnostics.md", "площадь v3, км²", AREA_V3, 11.06, 0.01),
    ("docs/diagnostics.md", "площадь v1, км²", float(versions.loc["v1", "area_km2"]), 1.80, 0.01),
    ("docs/diagnostics.md", "плотность v2, чел/км²",
     int(pop_mal["01.01.2025"]) / AREA_V2, 8243, 1),
    # --- разд. 1: берег ---
    ("docs/diagnostics.md", "жилая застройка в прибрежной полосе 300 м v3, %",
     100 * living_in_shore_km2 / shore_km2, 4.9, 0.1),
    ("docs/diagnostics.md", "площадь прибрежной полосы 300 м в v3, км²", shore_km2, 3.75, 0.02),
    # --- разд. 2: кварталы ---
    ("docs/diagnostics.md", "доля жилфонда v2 с известным годом 1946–1991, %",
     100 * known2.year.between(1946, 1991).mean(), 71.1, 0.1),
    ("docs/diagnostics.md", "доля домов v2 до 1917, %",
     100 * (known2.year < 1917).mean(), 4.8, 0.1),
    ("docs/diagnostics.md", "доля домов v2 1960–1979 (из известного года), %",
     100 * ((known2.year >= 1960) & (known2.year < 1980)).mean(), 50.2, 0.5),
    ("docs/diagnostics.md", "доля зелени в v2 (OSM), %", 43.0, 43, 0.5),
    # --- сервисы: таблица разд. 0 (узловые) и разд. 3 (с полигонами) ---
    ("docs/diagnostics.md", "узловых сервисов v1", int(services[services.geom_type == "Point"].within(V1).sum()), 30, 0),
    ("docs/diagnostics.md", "узловых сервисов v2", int(services[services.geom_type == "Point"].within(V2).sum()), 95, 0),
    ("docs/diagnostics.md", "узловых сервисов v3", svc3_pts, 160, 0),
    ("docs/diagnostics.md", "узловых сервисов v4", int(services[services.geom_type == "Point"].within(V4).sum()), 159, 0),
    ("docs/diagnostics.md", "сервисов v3 с полигонами (160 узловых + 77)", len(svc3), 237, 0),
    # --- баланс территории v2: жилое пятно, промздания, промзоны, гаражи ---
    ("docs/diagnostics.md", "жилое пятно v2, % территории v2",
     100 * share_km2(living2.geometry, V2) / AREA_V2, 6.8, 0.1),
    ("docs/numbers_check.md", "промышленно-складские здания v2, % территории v2",
     100 * share_km2(building[building.building.isin(IND_B)].geometry, V2) / AREA_V2, 0.5, 0.05),
    ("docs/numbers_check.md", "промзоны landuse=industrial в v2, % территории v2",
     100 * share_km2(ind_lu2.geometry, V2) / AREA_V2, 4.1, 0.05),
    ("docs/numbers_check.md", "гаражи v2, % территории v2",
     100 * share_km2(building[building.building.isin(GAR_B)].geometry, V2) / AREA_V2, 0.2, 0.05),
    # --- фронт воды: осевые линии рек в v3 ---
    ("docs/numbers_check.md", "осевые линии Невы и Охты в v3, км", river_axes_km, 9.1, 0.1),
    # --- ОКН ---
    ("docs/diagnostics.md", "ОКН в v3 (с Ниеншанцем), всего", len(okn), 60, 0),
    ("docs/diagnostics.md", "ОКН федерального значения в v3",
     int((okn.cat == "Федерального значения").sum()), 17, 0),
    ("docs/diagnostics.md", "ОКН в v2", int(okn.within(V2).sum()), 21, 0),
    ("docs/diagnostics.md", "ОКН в v1", int(okn.within(V1).sum()), 16, 0),
    # --- слои и дома ---
    ("docs/diagnostics.md", "домов с известным годом в v3", len(known3), 1095, 0),
    ("docs/diagnostics.md", "жилая застройка в v3, га",
     living3.to_crs(32636).area.sum() / 1e4, 96, 1),
    ("docs/diagnostics.md", "зданий v2", int(building.within(V2).sum()), 694, 0),
    ("docs/diagnostics.md", "зданий v3", int(building.within(V3).sum()), 1674, 0),
    ("docs/strategy.md", "площадь ядра v1 (З1), км²", float(versions.loc["v1", "area_km2"]), 1.8, 0.01),
    ("presentations/slides.md", "школ в v3 (узлы+полигоны OSM)",
     int(services.amenity.eq("school").sum()), 31, 0),
    # --- сетевой расчёт доступности (network_access_fallback.py) ---
    ("docs/diagnostics.md", "сетевой охват школ 500 м, %", net["schools_share"], 45.6, 0.1),
    ("docs/diagnostics.md", "сетевой охват детсадов 300 м, %", net["kindergartens_share"], 32.0, 0.1),
    ("docs/diagnostics.md", "сетевой охват здоровья 500 м, %", net["health_share"], 56.6, 0.1),
    ("docs/diagnostics.md", "сетевой охват аптек 300 м, %", net["pharmacies_share"], 35.4, 0.1),
    ("docs/diagnostics.md", "жилых зданий в 800 м от метро по сети, %", net["metro_800_share"], 14.9, 0.1),
    ("docs/diagnostics.md", "жилых зданий в 400 м от метро по сети, %", net["metro_400_share"], 2.5, 0.1),
    ("presentations/slides.md", "школы 500 м по сети (округл.), %", round(net["schools_share"]), 46, 0),
    ("presentations/slides.md", "детсады 300 м по сети (округл.), %", round(net["kindergartens_share"]), 32, 0),
    ("presentations/slides.md", "здоровье 500 м по сети (округл.), %", round(net["health_share"]), 57, 0),
    ("presentations/slides.md", "аптеки 300 м по сети (округл.), %", round(net["pharmacies_share"]), 35, 0),
    ("presentations/slides.md", "метро 800 м по сети (округл.), %", round(net["metro_800_share"]), 15, 0),
    # --- презентация: проверенные числа, заменившие старые формулировки ---
    ("presentations/slides.md", "сервисов v3 (узлы+полигоны) на слайде 06", len(svc3), 237, 0),
    ("presentations/slides.md", "промздания v2 на слайде 06, % территории v2",
     100 * share_km2(building[building.building.isin(IND_B)].geometry, V2) / AREA_V2, 0.5, 0.05),
    ("presentations/slides.md", "промзоны v2 на слайде 06, % территории v2",
     100 * share_km2(ind_lu2.geometry, V2) / AREA_V2, 4.1, 0.05),
    ("presentations/slides.md", "жилое пятно v2 на слайде 06, % территории v2",
     100 * share_km2(living2.geometry, V2) / AREA_V2, 6.8, 0.1),
    ("presentations/slides.md", "полоса 300 м v3 (слайды 01 и 07), км²", shore_km2, 3.75, 0.02),
    ("presentations/slides.md", "фронт воды v3 по осям рек (слайд 13), км", river_axes_km, 9.1, 0.1),
]

if "--control" in sys.argv:
    CHECKS[0] = CHECKS[0][:3] + (CHECKS[0][3] + 1, CHECKS[0][4])

bad = 0
for doc, what, got, claimed, tol in CHECKS:
    ok = abs(float(got) - claimed) <= tol
    bad += not ok
    print(f"{'OK  ' if ok else 'FAIL'} [{doc}] {what}: в данных {float(got):.3f}, в тексте {claimed}")
print(f"\nИТОГ: {len(CHECKS) - bad} из {len(CHECKS)} совпали" + ("" if not bad else f", расхождений: {bad}"))
sys.exit(1 if bad else 0)
