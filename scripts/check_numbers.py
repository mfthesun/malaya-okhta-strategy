"""check_numbers.py — пересчитывает числа из документов по данным репозитория.

Запуск:  python3 scripts/check_numbers.py            # проверка
         python3 scripts/check_numbers.py --control  # контроль: подставляет заведомо неверное значение, проверка ОБЯЗАНА упасть
Код выхода: 0 — все числа совпали; 1 — есть расхождения.
Числа из внешних источников (веб, документы вне репозитория) здесь не проверяются — см. docs/numbers_check.md.

Каждая строка CHECKS: (документ, утверждение, пересчитанное значение, заявленное значение, допуск).
Список наполняется по мере появления цифр в docs/ и слайдах.
"""
import sys
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parents[1]


def csv(p):
    for sep in (";", ","):
        d = pd.read_csv(R / p, sep=sep, encoding="utf-8-sig")
        if d.shape[1] > 1:
            return d
    raise ValueError(p)


# --- данные (этап 2) -------------------------------------------------------
# population = csv('data/raw/population_spb_mo_2010_2025.csv')

CHECKS = [
    # (документ, утверждение, пересчёт, заявлено, допуск)
    # Пример на старте: население МО Малая Охта, ряд Петростата.
    # ("docs/diagnostics.md", "население МО Малая Охта 01.01.2025, чел.",
    #  int(pop.loc[pop["Муниципальное образование"] == "МО Малая Охта", "2025"].iloc[0]), 43319, 0),
]


def main():
    if "--control" in sys.argv:
        if not CHECKS:
            print("Контроль невозможен: CHECKS пуст (этап 2 ещё не заполнил проверки).")
            return 1
        CHECKS[0] = CHECKS[0][:3] + (CHECKS[0][3] + 1, CHECKS[0][4])
    bad = 0
    for doc, what, got, claimed, tol in CHECKS:
        ok = abs(float(got) - claimed) <= tol
        bad += not ok
        print(f"{'OK  ' if ok else 'FAIL'} [{doc}] {what}: в данных {float(got):.3f}, в тексте {claimed}")
    print(f"\nИТОГ: {len(CHECKS) - bad} из {len(CHECKS)} совпали" + ("" if not bad else f", расхождений: {bad}"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
