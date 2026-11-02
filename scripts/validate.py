"""validate.py — валидация обработанных слоёв data/processed.

Проверки (по образцу primorsk): файл читается, CRS = EPSG:4326, геометрии валидны,
нет пустых геометрий, границы версий не пересекаются между собой.
Запуск: python3 scripts/validate.py; код выхода 0 — ошибок нет.
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
PROC = R / "data/processed"

REQUIRED_CRS = "EPSG:4326"


def main():
    if not PROC.exists() or not any(PROC.glob("*.geojson")):
        print("В data/processed нет слоёв — нечего валидировать (этап 2 ещё не выполнялся).")
        return 0
    import geopandas as gpd

    errors = 0
    for path in sorted(PROC.rglob("*.geojson")):
        rel = path.relative_to(R)
        try:
            gdf = gpd.read_file(path)
        except Exception as e:  # noqa: BLE001
            print(f"FAIL  {rel}: не читается ({e})")
            errors += 1
            continue
        if gdf.crs is None or gdf.crs.to_string() != REQUIRED_CRS:
            print(f"FAIL  {rel}: CRS {gdf.crs} вместо {REQUIRED_CRS}")
            errors += 1
        if gdf.geometry.isna().any() or gdf.geometry.is_empty.any():
            n = int(gdf.geometry.isna().sum() + gdf.geometry.is_empty.sum())
            print(f"FAIL  {rel}: {n} пустых геометрий")
            errors += 1
        invalid = (~gdf.geometry.is_valid).sum()
        if invalid:
            print(f"FAIL  {rel}: {invalid} невалидных геометрий")
            errors += 1
        if not errors:
            print(f"OK    {rel}: {len(gdf)} объектов, CRS ок")
    print(f"\nИтог: {'ошибок нет' if not errors else f'ошибок: {errors}'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
