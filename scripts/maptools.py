"""Единый макет карт проекта «Малая Охта»: поле карты, легенда, указатель севера, линейка.

Адаптация scripts/maptools.py из репозитория altai-spatial-planning под СПб:
метрический CRS по умолчанию — UTM 36N (EPSG:32636), сближение меридианов ~2,4°.

    fig, ax = map_figure()
    ... рисуем слои в EPSG:32636 ...
    finish(fig, ax, extent=(x0, y0, x1, y1), handles=[...], basemap="imagery")
    save_map(fig, path)

Все карты одного размера, оформление на одних местах — вставка в слайды без подгонки.
Заголовков на картах нет: заголовок слайда и подпись к рисунку задаёт презентация.
Подложка обязательна — тайлы Esri без подписей (подписи на карте только наши).
"""
import math
import re
import textwrap

import contextily as cx
import matplotlib.patheffects as pe
import xyzservices.providers as xyz
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Rectangle
from pyproj import Transformer

FIG_SIZE = (10, 7)                    # дюймы; при DPI 200 — 2000 × 1400 px
DPI = 200
MAP_RECT = (0.01, 0.015, 0.69, 0.97)  # поле карты в долях рисунка: x, y, ширина, высота
LEGEND_ANCHOR = (0.715, 0.985)        # левый верхний угол условных обозначений
NORTH_LOC = (0.955, 0.875)            # основание стрелки севера, доли поля карты
SCALE_LOC = (0.035, 0.035)            # левый нижний угол линейки
SCALE_FRAC = 0.25
# Для района масштаба единиц км шкала «круглых» значений ниже; NICE_KM Алтая начинались с 2 км.
NICE_KM = [0.2, 0.5, 1, 2, 4, 10, 20, 50]
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#ffffff"
HALO = [pe.withStroke(linewidth=2.5, foreground=SURFACE)]
TITLE_WRAP, LABEL_WRAP = 34, 34
ATTR_LOC = (0.995, 0.006)
# Подложки Esri только без подписей: надписи на картах — наши и на русском.
BASEMAPS = {
    # публичный CartoDB Positron без подписей, @2x — двойное разрешение тайлов
    "positron": (xyz.Esri.WorldGrayCanvas,
                 "© Esri, World Gray Canvas; источники: Esri, HERE, Garmin, FAO, NOAA, USGS"),
    "relief": (xyz.Esri.WorldShadedRelief, "© Esri, World Shaded Relief; источник: Esri"),
    "imagery": (xyz.Esri.WorldImagery, "© Esri, World Imagery; источники: Esri, i-cubed, USDA, USGS, AEX, GeoEye, "
                                       "Getmapping, Aerogrid, IGN, IGP, UPR-EGP и сообщество пользователей ГИС"),
    "gray": (xyz.Esri.WorldGrayCanvas, "© Esri, World Gray Canvas; источники: Esri, HERE, Garmin, FAO, NOAA, USGS"),
}

SHORT = re.compile(r"(?<![\w-])([\w№]{1,2}) ")
NUM = re.compile(r"(\d) (?=[^\s—–])")


def _wrap(text, width):
    """Перенос по словам; после коротких слов и чисел — неразрывный пробел, «—» не начинает строку."""
    lines = (NUM.sub("\\1\u00a0", SHORT.sub("\\1\u00a0", line)).replace(" —", "\u00a0—") for line in text.split("\n"))
    return "\n".join(textwrap.fill(line, width) for line in lines)


MAP_RECT_FULL = (0.0, 0.0, 1.0, 1.0)  # полнокадровое поле: изображение = карта без белых полей


def map_figure(full=False):
    """Рисунок стандартного размера; full=True — карта занимает весь кадр, легенда поверх."""
    fig = plt.figure(figsize=FIG_SIZE)
    rect = MAP_RECT_FULL if full else MAP_RECT
    ax = fig.add_axes(rect)
    ax.set_axis_off()
    ax._maptools_rect = rect  # исходная рамка: geopandas-слои её искажают через aspect='equal'
    return fig, ax


def set_extent(ax, x0, y0, x1, y1):
    """Охват карты, расширенный до пропорций поля: масштаб по осям одинаковый."""
    # geopandas-слой ставит aspect='equal' и подгоняет рамку осей; вернуть исходную
    # рамку и aspect до расчёта, иначе пропорция поля считается по искажённой рамке
    if hasattr(ax, "_maptools_rect"):
        ax.set_position(ax._maptools_rect)
    ax.set_aspect("auto")
    fw, fh = ax.figure.get_size_inches()
    rect = ax.get_position()
    box = (rect.height * fh) / (rect.width * fw)
    w, h = x1 - x0, y1 - y0
    cx_, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if h / w < box:
        h = w * box
    else:
        w = h / box
    ax.set_xlim(cx_ - w / 2, cx_ + w / 2)
    ax.set_ylim(cy - h / 2, cy + h / 2)


def scale_bar(ax, loc=SCALE_LOC, frac=SCALE_FRAC, segments=4, fontsize=7.5):
    """Линейка из чередующихся чёрно-белых отрезков; длина — «круглое» число км."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    w, h = x1 - x0, y1 - y0
    km = max([k for k in NICE_KM if k * 1000 <= frac * w] or NICE_KM[:1])
    seg = km * 1000 / segments
    bx, by = x0 + loc[0] * w, y0 + loc[1] * h
    bh = 0.011 * h
    ax.add_patch(Rectangle((bx - 0.015 * w, by - 0.012 * h), km * 1000 + 0.05 * w, bh + 0.055 * h,
                           facecolor=SURFACE, edgecolor="none", alpha=0.85, zorder=19))
    for i in range(segments):
        ax.add_patch(Rectangle((bx + i * seg, by), seg, bh, facecolor=INK if i % 2 == 0 else SURFACE,
                               edgecolor=INK, lw=0.6, zorder=20))
    for i, lab in [(0, "0"), (segments // 2, f"{km / 2:g}"), (segments, f"{km:g} км")]:
        ax.text(bx + i * seg, by + bh * 1.8, lab, ha="center", va="bottom", fontsize=fontsize, color=INK,
                path_effects=HALO, zorder=21)


def north_arrow(ax, crs=32636, loc=NORTH_LOC, size=0.07, fontsize=10):
    """Условный север: вертикальная стрелка с буквой «С» (без сближения меридианов)."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    w, h = x1 - x0, y1 - y0
    L = size * h
    bx, by = x0 + loc[0] * w, y0 + loc[1] * h
    ax.add_patch(FancyArrow(bx, by, 0, L, width=L * 0.12, head_width=L * 0.42, head_length=L * 0.45,
                            length_includes_head=True, color=INK, zorder=20, path_effects=HALO))
    ax.text(bx, by + L * 1.25, "С", ha="center", va="bottom", fontsize=fontsize, fontweight="bold",
            color=INK, path_effects=HALO, zorder=21)


def basemap(ax, style="imagery", crs=32636, alpha=1.0, zoom=None):
    """Подложка Esri под всеми слоями и её атрибуция в правом нижнем углу поля.

    zoom=None — авто; принудительный зум выше авто даёт более чёткие тайлы.
    """
    src, attribution = BASEMAPS[style]
    kw = {} if zoom is None else {"zoom": zoom}
    cx.add_basemap(ax, crs=f"EPSG:{crs}", source=src, attribution=False, zorder=-10,
                   reset_extent=True, alpha=alpha, **kw)
    ax.text(*ATTR_LOC, f"Подложка: {attribution}", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=5.5, color=MUTED, path_effects=HALO, zorder=21, wrap=True)


def finish(fig, ax, extent, handles, title="Условные обозначения", crs=32636, basemap_style="imagery",
           basemap_alpha=1.0, legend_on_map=True, basemap_zoom=None):
    """Охват, подложка, указатель севера, линейка и легенда.

    legend_on_map=True: карта на весь кадр, легенда в правом НИЖНЕМ углу поля карты на
    полупрозрачной белой подложке; стрелка севера в левом верхнем углу.
    legend_on_map=False: легенда справа за полем карты (на paper-подложке).
    """
    set_extent(ax, *extent)
    keep_xlim, keep_ylim = ax.get_xlim(), ax.get_ylim()  # basemap(reset_extent=True) расширяет охват до тайлов
    basemap(ax, basemap_style, crs, basemap_alpha, zoom=basemap_zoom)
    ax.set_xlim(keep_xlim); ax.set_ylim(keep_ylim)
    for hd in handles:
        hd.set_label(_wrap(hd.get_label(), LABEL_WRAP))
    if legend_on_map:
        north_arrow(ax, crs=crs, loc=(0.045, 0.875))
        scale_bar(ax)
        leg = fig.legend(handles=handles, loc="lower right", bbox_to_anchor=(0.992, 0.032), frameon=False,
                         fontsize=8, title=_wrap(title, TITLE_WRAP), title_fontsize=9,
                         alignment="left", labelspacing=0.55, handlelength=1.8)
        leg.set_zorder(40)
        fig.canvas.draw()
        bb = leg.get_window_extent()
        inv = fig.transFigure.inverted()
        (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
        pad = 0.008
        back = fig.add_artist(Rectangle((x0 - pad, y0 - pad), x1 - x0 + 2 * pad, y1 - y0 + 2 * pad,
                             transform=fig.transFigure, facecolor=SURFACE, alpha=0.82, edgecolor="none",
                             zorder=39))
    else:
        fig.legend(handles=handles, loc="upper left", bbox_to_anchor=LEGEND_ANCHOR, frameon=False, fontsize=8,
                   title=_wrap(title, TITLE_WRAP), title_fontsize=9, alignment="left", labelspacing=0.7,
                   handlelength=2.2)


def no_yo(fig):
    """В презентации пишем «е» вместо «ё» — во всех надписях рисунка."""
    for t in fig.findobj(lambda a: hasattr(a, "get_text") and hasattr(a, "set_text")):
        s = t.get_text()
        if "ё" in s or "Ё" in s:
            t.set_text(s.replace("ё", "е").replace("Ё", "Е"))


def save_map(fig, path):
    """Без обрезки по содержимому: все карты одного размера."""
    no_yo(fig)
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
