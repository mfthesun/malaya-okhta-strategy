"""process.py — обработка исходных слоёв data/raw → data/processed.

Конвенции (AGENTS.md): хранение EPSG:4326 GeoJSON, utf-8-sig, snake_case.
Слои района: boundary (версии границ), building, blocks, roads, water, green, landuse, okn, services.
Запуск: python3 scripts/process.py
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
RAW, PROC = R / "data/raw", R / "data/processed"


def main():
    if not RAW.exists() or not any(RAW.iterdir()):
        print("data/raw пуст — сначала наполните каталог (см. docs/data_catalog.md, notebook 02).")
        return 0
    # TODO(этап 2): заполнить по мере появления слоёв в data/raw.
    print("Обработчики слоёв будут добавлены на этапе 2 (диагностика).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
