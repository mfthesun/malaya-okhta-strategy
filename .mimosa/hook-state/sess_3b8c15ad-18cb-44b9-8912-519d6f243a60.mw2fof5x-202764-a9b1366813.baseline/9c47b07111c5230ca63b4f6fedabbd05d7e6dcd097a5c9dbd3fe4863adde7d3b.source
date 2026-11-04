// build_deck.js — черновая презентация «Стратегия развития Малой Охты 2027–2035»
// Палитра от темы района: вода/Охта. Карты из notebooks/maps_out (2000×1400).
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 × 7.5
pres.author = "Команда проекта (ИТМО)";
pres.title = "Стратегия развития Малой Охты 2027–2035";

const W = 13.33, H = 7.5, M = 0.55;
const BG = "F4F7FA", PRIMARY = "1F4E79", ACCENT = "B33A2B", TEXT = "1A2430", MUTED = "5B6B7B";
const LIGHT = "C7D9EA", SAND = "C98D3A";
const F = "Inter";
const MAPS = "../notebooks/maps_out/"; // запуск из presentations/, карты в корневом notebooks

const bu = () => ({ code: "2013", indent: 12 });

function header(s, kicker, title) {
  s.background = { color: BG };
  s.addText(kicker.toUpperCase(), { x: M, y: 0.32, w: 9, h: 0.3, fontSize: 12, fontFace: F,
    color: ACCENT, charSpacing: 3, bold: true, margin: 0 });
  s.addText(title, { x: M, y: 0.62, w: W - 2 * M, h: 0.85, fontSize: 30, fontFace: F, bold: true,
    color: TEXT, margin: 0 });
}

function mapImg(s, path, x, y, w) {
  const h = w * 0.7; // 2000×1400
  s.addShape(pres.shapes.RECTANGLE, { x: x - 0.06, y: y - 0.06, w: w + 0.12, h: h + 0.12,
    fill: { color: "FFFFFF" }, line: { color: "D5DEE6", width: 1 },
    shadow: { type: "outer", color: "000000", blur: 7, offset: 2, angle: 90, opacity: 0.14 } });
  s.addImage({ path, x, y, w, h, sizing: { type: "cover", w, h } });
  return h;
}

function source(s, text) {
  s.addText("Источник: " + text, { x: M, y: H - 0.42, w: W - 2 * M, h: 0.3, fontSize: 11,
    fontFace: F, color: MUTED, margin: 0 });
}

function stat(s, x, y, w, num, label, color) {
  s.addText(num, { x, y, w, h: 0.95, fontSize: 54, fontFace: F, bold: true, color: color || PRIMARY, margin: 0 });
  s.addText(label, { x, y: y + 0.95, w, h: 0.75, fontSize: 13.5, fontFace: F, color: MUTED, margin: 0 });
}

// ---------- 01 Титул ----------
let s = pres.addSlide();
s.background = { color: PRIMARY };
s.addImage({ path: MAPS + "01_boundaries.png", x: 6.6, y: 0, w: 6.73, h: 7.5,
  sizing: { type: "cover", w: 6.73, h: 7.5 }, transparency: 22 });
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 6.8, h: H, fill: { color: PRIMARY, transparency: 42 } });
s.addText("ФОРМИРОВАНИЕ ПРОСТРАНСТВЕННОГО ВИДЕНИЯ ГОРОДА · ИТМО", { x: M, y: 1.55, w: 6, h: 0.35,
  fontSize: 13, fontFace: F, color: LIGHT, charSpacing: 2.5, margin: 0 });
s.addText("Малая Охта:\nдве реки — общий берег", { x: M, y: 2.1, w: 6.1, h: 2.2, fontSize: 44,
  fontFace: F, bold: true, color: "FFFFFF", margin: 0 });
s.addText("Стратегия развития района 2027–2035", { x: M, y: 4.35, w: 6, h: 0.5, fontSize: 20,
  fontFace: F, color: "FFFFFF", margin: 0 });
s.addText("Команда: Денис Яковлев (руководитель) и соавторы · Санкт-Петербург", { x: M, y: 6.6, w: 6.2,
  h: 0.4, fontSize: 13, fontFace: F, color: LIGHT, margin: 0 });

// ---------- 02 Гипотезы ----------
s = pres.addSlide();
header(s, "Как всё началось", "Четыре гипотезы команды");
const hyp = [
  ["01", "Доступ к воде", "Два километра берега двух рек — и ни одного общественного места у воды"],
  ["02", "Внутриквартальное пространство", "Суперблоки 1946–1991 с пустой серединой: дворы, гаражи, разорванная зелень"],
  ["03", "«А где все люди?»", "Плотность 8 200 чел/км², но район убывает и выглядит пустым"],
  ["04", "Приезжие и местные", "Заводские сообщества и новые арендаторы не пересекаются"],
];
hyp.forEach((h, i) => {
  const y = 1.75 + i * 1.28;
  s.addText(h[0], { x: M, y, w: 0.9, h: 0.9, fontSize: 40, fontFace: F, bold: true, color: LIGHT, margin: 0 });
  s.addText(h[1], { x: M + 1.05, y, w: 4.4, h: 0.9, fontSize: 19, fontFace: F, bold: true, color: PRIMARY,
    valign: "middle", margin: 0 });
  s.addText(h[2], { x: 6.15, y, w: W - 6.15 - M, h: 0.9, fontSize: 14.5, fontFace: F, color: TEXT,
    valign: "middle", margin: 0 });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: M, y: y + 1.08, w: W - 2 * M, h: 0,
    line: { color: "D5DEE6", width: 1 } });
});
s.addNotes("Гипотезы сформулированы командой при обсуждении; каждая проверяется данными далее.");

// ---------- 03 Границы ----------
s = pres.addSlide();
header(s, "Территория", "У района нет одной границы — работаем с четырьмя");
mapImg(s, MAPS + "01_boundaries.png", 0.9, 1.75, 6.9);
stat(s, 8.35, 1.8, 4.3, "1,80 → 11,06 км²", "от исторического ядра (v1) до всей административной Охты (v3)");
stat(s, 8.35, 3.55, 4.3, "4 версии", "вложены на 100 %: ядро ⊂ МО Малая Охта ⊂ вся Охта; полуостров — линза поверх");
stat(s, 8.35, 5.3, 4.3, "43 319", "жителей в МО Малая Охта (01.01.2025) — базовая аналитическая единица", ACCENT);
source(s, "OSM relations 1185381/1185383; расчёт notebooks/01; приём «версий границ» — проект «Коломна»");

// ---------- 04 Люди: ряд ----------
s = pres.addSlide();
header(s, "Демография", "Малая Охта — единственное из двух охтинских МО, теряющее людей");
s.addChart(pres.charts.LINE, [
  { name: "МО Малая Охта", labels: ["2010 (ВПН)", "2018", "2019", "2020", "2021 (ВПН)", "2023", "2024", "2025"],
    values: [45946, 48092, 47932, 47703, 43849, 43414, 43157, 43319] },
  { name: "МО Большая Охта", labels: ["2010 (ВПН)", "2018", "2019", "2020", "2021 (ВПН)", "2023", "2024", "2025"],
    values: [54539, 57068, 56848, 56658, 58616, 58140, 57831, 58176] },
], { x: M, y: 1.75, w: 7.6, h: 4.7, chartColors: [ACCENT, PRIMARY], lineSize: 3,
  catAxisLabelColor: MUTED, valAxisLabelColor: MUTED, valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendColor: MUTED,
  valAxisMinVal: 40000, valAxisMaxVal: 62000, fontFace: F, dataLabelColor: TEXT });
stat(s, 8.55, 1.85, 4.2, "−5,7 %", "Малая Охта, 2010 → 2025");
stat(s, 8.55, 3.5, 4.2, "+6,7 %", "Большая Охта за тот же срок — сосед растёт");
stat(s, 8.55, 5.15, 4.2, "+9,3 %", "Красногвардейский район в целом", ACCENT);
source(s, "Петростат/ВПН (notebooks/01); скачок 2022→2023 — пересчёт по итогам ВПН-2020, не тренд");

// ---------- 05 Возраст ----------
s = pres.addSlide();
header(s, "Морфология", "Индустриальный район: 71 % домов — 1946–1991");
mapImg(s, MAPS + "02_house_age.png", 6.0, 1.75, 6.6);
stat(s, M, 1.8, 4.9, "4,8 %", "домов построено до 1917 — историческая ткань тонка");
stat(s, M, 3.35, 4.9, "50 %", "жилфонда с известным годом — 1961–1980 (массовые серии)");
stat(s, M, 4.9, 4.9, "43 %", "территории v2 — зелень, но она не организована как каркас");
source(s, "«Карта возраста домов» (HOITH), notebooks/02–03");

// ---------- 06 Загадка ----------
s = pres.addSlide();
header(s, "Загадка района", "Плотность 8 200 чел/км², а район «пустой»");
s.addText("Формула загадки — четыре слагаемых:", { x: M, y: 1.7, w: 9, h: 0.4, fontSize: 16,
  fontFace: F, color: MUTED, margin: 0 });
stat(s, M, 2.3, 2.9, "−5,7 %", "населения за 15 лет — при растущем районе");
stat(s, 3.75, 2.3, 2.9, "6,8 %", "территории v2 — жилое пятно; суперблоки вокруг");
stat(s, 7.0, 2.3, 2.9, "0,5 %", "промышленно-складской застройки — рабочих мест рядом почти нет");
stat(s, 10.2, 2.3, 2.6, "15 %", "жилых зданий в 800 м пешком по сети от метро", ACCENT);
s.addShape(pres.shapes.RECTANGLE, { x: M, y: 4.6, w: W - 2 * M, h: 1.6, fill: { color: "E8EEF4" } });
s.addText([
  { text: "«Приезжие и местные»:", options: { bold: true, color: PRIMARY, breakLine: true } },
  { text: "заводские сообщества Охты и новые арендаторы не пересекаются — нет мест встречи и общих общественных пространств.", options: {} },
], { x: M + 0.25, y: 4.75, w: W - 2 * M - 0.5, h: 1.3, fontSize: 15, fontFace: F, color: TEXT, margin: 0 });
source(s, "notebooks/01, 03; Петростат/ВПН");

// ---------- 07 Берег ----------
s = pres.addSlide();
header(s, "Проблема 1", "В 300 м от воды живёт меньше всего людей");
mapImg(s, MAPS + "05_landuse.png", 0.9, 1.75, 6.9);
stat(s, 8.35, 1.8, 4.3, "4 %", "прибрежной полосы (2,49 км² в v3) занято жилой застройкой", ACCENT);
stat(s, 8.35, 3.55, 4.3, "0", "общественных пространств у воды; мыc с Ниеншанцем — огороженный раскоп");
stat(s, 8.35, 5.3, 4.3, "60 ОКН", "(17 федеральных) — каркас идентичности без публичного адреса");
source(s, "notebooks/03; слой промзон OSM неполон — нижняя оценка, сверка с ФГИС ТП — следующий шаг");

// ---------- 08 Середина ----------
s = pres.addSlide();
header(s, "Проблема 2", "Квартал есть — середины нет");
mapImg(s, MAPS + "04_services.png", 0.9, 1.75, 6.9);
stat(s, 8.35, 1.55, 4.3, "46 %", "жилых зданий в 500 м от школы — пешком по сети (v3)");
stat(s, 8.35, 2.9, 4.3, "32 %", "в 300 м от детсада по сети — дыры внутри суперблоков");
stat(s, 8.35, 4.25, 4.3, "57 %", "в 500 м от объектов здоровья по сети");
stat(s, 8.35, 5.55, 4.3, "35 %", "в 300 м от аптеки по сети");
source(s, "Сетевой расчёт: граф 37 тыс. узлов из OSM-дорог (network_access_fallback.py, networkx); notebooks/03");

// ---------- 09 Мировой опыт ----------
s = pres.addSlide();
header(s, "Аналоги", "Восемь кейсов районных стратегий — двенадцать принципов");
const cases = [
  ["HafenCity, Гамбург", "единая девелоперская компания, value capture, доступ к воде в каждом квартале"],
  ["Bilbao Ría 2000", "агентство-координатор из ~10 человек; земля как актив замыкает финансирование"],
  ["King's Cross, Лондон", "консент-план с гибкостью ±20 %; якорные институции; цена — джентрификация"],
  ["Nordhavn, Копенгаген", "«5-минутный город»: круги 400 м от метро задают плотность"],
  ["22@ Barcelona", "зонирование как драйвер; урок: долю жилья закладывать сразу, а не ревизией"],
  ["Nieuw-West, Амстердам", "бережная реновация 1950–60-х; право возвращения; физика ≠ качество жизни"],
  ["197-a plans, NYC", "сообщество — соавтор районного плана: резерв проектов"],
  ["СПб: КРТ-2026, «серый пояс»", "правовая рамка, в которую стратегия встраивается напрямую"],
];
cases.forEach((c, i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = M + col * 6.2, y = 1.7 + row * 1.22;
  s.addText(c[0], { x, y, w: 5.9, h: 0.35, fontSize: 15.5, fontFace: F, bold: true, color: PRIMARY, margin: 0 });
  s.addText(c[1], { x, y: y + 0.35, w: 5.9, h: 0.65, fontSize: 12.5, fontFace: F, color: TEXT, margin: 0 });
});
source(s, "docs/world_cases.md — полные кейсы с источниками и сводной таблицей «принцип → применимость»");

// ---------- 10 Миссия ----------
s = pres.addSlide();
s.background = { color: PRIMARY };
s.addText("МИССИЯ", { x: M, y: 1.35, w: 6, h: 0.4, fontSize: 13, fontFace: F, color: LIGHT,
  charSpacing: 3, margin: 0 });
s.addText("«Малая Охта:\nдве реки — общий берег»", { x: M, y: 1.9, w: 11.5, h: 1.9, fontSize: 40,
  fontFace: F, bold: true, color: "FFFFFF", margin: 0 });
s.addText("Видение 2035", { x: M, y: 4.15, w: 6, h: 0.4, fontSize: 15, fontFace: F, bold: true,
  color: SAND, margin: 0 });
s.addText([
  { text: "берег — в 10 минутах пешком от каждой семьи", options: { bullet: bu(), breakLine: true } },
  { text: "середины кварталов работают: сеть дворовых пространств", options: { bullet: bu(), breakLine: true } },
  { text: "люди остаются днём: ≥ 5 000 новых рабочих мест в КРТ", options: { bullet: bu(), breakLine: true } },
  { text: "«местные» и «приезжие» встречаются на маршруте «Ниеншанц — Охта»", options: { bullet: bu() } },
], { x: M, y: 4.6, w: 11, h: 2.2, fontSize: 17, fontFace: F, color: "FFFFFF", paraSpaceAfter: 8, margin: 0 });

// ---------- 11 Модель ----------
s = pres.addSlide();
header(s, "Пространственная модель", "Четыре зоны, четыре узла, четыре каркаса");
mapImg(s, MAPS + "01_boundaries.png", 0.9, 1.75, 6.9);
const zones = [
  ["З1 «Мыс»", "музейно-общественное ядро — флагман 1-й очереди"],
  ["З2 «Берег Охты»", "набережная + КРТ промзон со смешанными функциями"],
  ["З3 «Суперблоки»", "режим наполнения: дворы, сервисы, зелёный каркас"],
  ["З4 «Восточный резерв»", "рекреационное развитие 3-й очереди"],
];
zones.forEach((z, i) => {
  const y = 1.75 + i * 0.95;
  s.addText(z[0], { x: 8.35, y, w: 4.3, h: 0.32, fontSize: 15.5, fontFace: F, bold: true, color: PRIMARY, margin: 0 });
  s.addText(z[1], { x: 8.35, y: y + 0.32, w: 4.3, h: 0.55, fontSize: 12.5, fontFace: F, color: TEXT, margin: 0 });
});
s.addText("Узлы: мыc · «Новочеркасская» · «Ладожская» · Уткина дача. Каркасы: водно-общественный, зелёно-пешеходный, сервисный, историко-культурный.",
  { x: 8.35, y: 5.6, w: 4.3, h: 1.0, fontSize: 12, fontFace: F, color: MUTED, margin: 0 });
source(s, "docs/strategy.md, разд. 4");

// ---------- 12 А Вода ----------
s = pres.addSlide();
header(s, "Направление А", "Вода: общественная ось Невы и Охты");
const aItems = [
  ["А1 · 2027", "конкурс концепций «Берег Охты» — мастер-план берега"],
  ["А2 · 2029–2035", "очереди набережных: пилот 800 м у мыса → непрерывность"],
  ["А3 · 2029", "«Ниеншанц-парк»: музеефикация раскопа + площадь + берег"],
  ["А4 · 2027–2035", "6–8 «порталов к воде» из кварталов (каждые 400–500 м)"],
];
aItems.forEach((a, i) => {
  const y = 1.75 + i * 1.05;
  s.addText(a[0], { x: M, y, w: 2.4, h: 0.8, fontSize: 14, fontFace: F, bold: true, color: ACCENT, margin: 0 });
  s.addText(a[1], { x: 3.1, y, w: 5.4, h: 0.8, fontSize: 14.5, fontFace: F, color: TEXT, margin: 0 });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: M, y: y + 0.9, w: 7.9, h: 0, line: { color: "D5DEE6", width: 1 } });
});
stat(s, 9.0, 1.8, 3.8, "≥ 60 %", "берега в v3 — общественная функция к 2035 (Ц1)", ACCENT);
stat(s, 9.0, 4.0, 3.8, "2029", "первый общественный берег района — «Ниеншанц-парк»");
s.addText("Кейсы: HafenCity (доступ к воде), Bilbao (якорь на воде), King's Cross (Granary Square)",
  { x: 9.0, y: 5.9, w: 3.8, h: 0.9, fontSize: 11.5, fontFace: F, color: MUTED, margin: 0 });

// ---------- 13 Б Кварталы ----------
s = pres.addSlide();
header(s, "Направление Б", "Кварталы: наполнить середину");
const bItems = [
  ["Б1", "«Середина квартала»: 4–6 дворов в очередь — в «пустые» ячейки плотности"],
  ["Б2", "гаражные массивы → двор-парк + многоуровневая парковка (2–3 площадки)"],
  ["Б3", "сервисы по дырам охвата: школы, детсады, здоровье — по буферному дефициту"],
  ["Б4", "«Охтинская Groene As»: зелёно-пешеходный маршрут дворы → парки → Оккервиль"],
];
bItems.forEach((a, i) => {
  const y = 1.75 + i * 1.05;
  s.addText(a[0], { x: M, y, w: 0.8, h: 0.8, fontSize: 16, fontFace: F, bold: true, color: ACCENT, margin: 0 });
  s.addText(a[1], { x: 1.5, y, w: 7.0, h: 0.8, fontSize: 14.5, fontFace: F, color: TEXT, margin: 0 });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: M, y: y + 0.9, w: 7.9, h: 0, line: { color: "D5DEE6", width: 1 } });
});
stat(s, 9.0, 1.8, 3.8, "≥ 80 %", "жилых зданий в 300 м от общественного пространства (Ц2)");
stat(s, 9.0, 3.9, 3.8, "≥ 90 %", "жилых зданий в 500 м от школы к 2035");
s.addText("Кейсы: Nieuw-West (плотизация, Groene As), Nordhavn (5-минутный центр)",
  { x: 9.0, y: 5.9, w: 3.8, h: 0.9, fontSize: 11.5, fontFace: F, color: MUTED, margin: 0 });

// ---------- 14 В+Г ----------
s = pres.addSlide();
header(s, "Направления В и Г", "Люди днём в районе · общая идентичность");
s.addText("В. «Люди»", { x: M, y: 1.7, w: 5.8, h: 0.4, fontSize: 17, fontFace: F, bold: true, color: PRIMARY, margin: 0 });
s.addText([
  { text: "2–3 площадки КРТ с фиксированным миксом: жильё ≥ 40 %, соцобъекты ≥ 10 %", options: { bullet: bu(), breakLine: true } },
  { text: "якорный институт у мыса (кампус / медиа-кластер / музей)", options: { bullet: bu(), breakLine: true } },
  { text: "программа «Первый этаж» для уличного малого бизнеса", options: { bullet: bu(), breakLine: true } },
  { text: "цель: ≥ 5 000 рабочих мест; население v2 ≥ 45 000 к 2035", options: { bullet: bu() } },
], { x: M, y: 2.15, w: 5.8, h: 3.6, fontSize: 14, fontFace: F, color: TEXT, paraSpaceAfter: 8, margin: 0 });
s.addText("Г. «Мы и свои»", { x: 7.0, y: 1.7, w: 5.8, h: 0.4, fontSize: 17, fontFace: F, bold: true, color: PRIMARY, margin: 0 });
s.addText([
  { text: "ежегодный партисипационный цикл: игра «Город на развилке» → конкурс → реализация (≥ 4 события/год)", options: { bullet: bu(), breakLine: true } },
  { text: "маршрут идентичности «Ниеншанц — Охта»: навигация, аудиогид, Графтио и заводы", options: { bullet: bu(), breakLine: true } },
  { text: "микрогранты местных инициатив; право возвращения жителей в КРТ-проектах", options: { bullet: bu(), breakLine: true } },
  { text: "сохранение ≥ 60 % жилфонда 1946–1991 (без сплошного сноса)", options: { bullet: bu() } },
], { x: 7.0, y: 2.15, w: 5.8, h: 3.6, fontSize: 14, fontFace: F, color: TEXT, paraSpaceAfter: 8, margin: 0 });
s.addText("Кейсы: 22@ (+ урок ревизии 2022), King's Cross (якоря), 197-a (соавторство), Nieuw-West (право возвращения)",
  { x: M, y: 6.35, w: W - 2 * M, h: 0.4, fontSize: 11.5, fontFace: F, color: MUTED, margin: 0 });

// ---------- 15 Флагманы ----------
s = pres.addSlide();
header(s, "Флагманы", "Три проекта, проводящие стратегию");
const flags = [
  ["2027–2030", "Охтинский мыс:\nНиеншанц", "музеефикация раскопа, общественная площадь, участок набережной Невы, порталы в кварталы. Аналоги: Bilbao, HafenCity"],
  ["2029–2035", "Водная ось:\nот мыса до Оккервиля", "непрерывная пешеходно-велосипедная ось вдоль Охты, очереди набережных. Аналоги: King's Cross, Nieuw-West"],
  ["2027–2035", "Середина\nквартала", "итерационная программа дворов, гаражей и сервисов. Аналоги: Nieuw-West, Nordhavn"],
];
flags.forEach((f, i) => {
  const x = M + i * 4.15;
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.8, w: 3.85, h: 4.6, fill: { color: "FFFFFF" },
    line: { color: "D5DEE6", width: 1 }, shadow: { type: "outer", color: "000000", blur: 7, offset: 2, angle: 90, opacity: 0.12 } });
  s.addText(f[0], { x: x + 0.25, y: 2.0, w: 3.35, h: 0.35, fontSize: 13, fontFace: F, bold: true, color: ACCENT, margin: 0 });
  s.addText(f[1], { x: x + 0.25, y: 2.45, w: 3.35, h: 1.25, fontSize: 21, fontFace: F, bold: true, color: PRIMARY, margin: 0 });
  s.addText(f[2], { x: x + 0.25, y: 3.85, w: 3.35, h: 2.3, fontSize: 12.5, fontFace: F, color: TEXT, margin: 0 });
});
source(s, "docs/strategy.md, разд. 6; бюджетная логика — город + КРТ + федеральные программы наследия");

// ---------- 16 Дорожная карта ----------
s = pres.addSlide();
header(s, "Дорожная карта", "Три очереди: каждая заканчивается общественным объектом");
const stages = [
  ["1-я очередь", "2027–2029", ["конкурс «Берег Охты»", "пилот «Середины квартала» (2 двора)", "маршрут «Ниеншанц — Охта»", "открытие «Ниеншанц-парка»"]],
  ["Среднесрочный этап", "2030–2032", ["очереди набережной Охты", "первые 2 площадки КРТ", "якорный институт у мыса", "микрогранты, реорганизация гаражей"]],
  ["Расчётный срок", "2033–2035", ["≥ 60 % берега — общественная функция", "3-я площадка КРТ", "зелёный каркас до Оккервиля", "итоговый мониторинг Ц1–Ц4"]],
];
stages.forEach((st, i) => {
  const x = M + i * 4.15;
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.9, w: 3.85, h: 0.75, fill: { color: i === 0 ? ACCENT : PRIMARY } });
  s.addText(st[1] + " · " + st[0], { x: x + 0.2, y: 1.9, w: 3.5, h: 0.75, fontSize: 15, fontFace: F,
    bold: true, color: "FFFFFF", valign: "middle", margin: 0 });
  s.addText(st[2].map((t, j) => ({ text: t, options: { bullet: bu(), breakLine: j < st[2].length - 1 } })),
    { x, y: 2.95, w: 3.85, h: 3.6, fontSize: 13, fontFace: F, color: TEXT, paraSpaceAfter: 8, margin: 0, valign: "top" });
});
source(s, "docs/strategy.md, разд. 9");

// ---------- 17 Механизм ----------
s = pres.addSlide();
header(s, "Реализация", "Штаб-координатор, инструменты КРТ, открытый мониторинг");
s.addText("Механизм", { x: M, y: 1.7, w: 5.8, h: 0.4, fontSize: 16, fontFace: F, bold: true, color: PRIMARY, margin: 0 });
s.addText([
  { text: "координационный штаб: район + КГА + КГИОП + МО + сообщество (модель Bilbao Ría 2000: 10–11 человек, координация, не девелопмент)", options: { bullet: bu(), breakLine: true } },
  { text: "инструменты: КРТ (494-ФЗ, в СПб с 2026), «серый пояс», конкурсы концепций", options: { bullet: bu(), breakLine: true } },
  { text: "финансирование: город + обязательства девелоперов + федеральные программы наследия", options: { bullet: bu() } },
], { x: M, y: 2.15, w: 5.8, h: 3.2, fontSize: 13.5, fontFace: F, color: TEXT, paraSpaceAfter: 8, margin: 0 });
s.addText("Риски и митигации", { x: 7.0, y: 1.7, w: 5.8, h: 0.4, fontSize: 16, fontFace: F, bold: true, color: PRIMARY, margin: 0 });
const risks = [
  ["снос вместо реновации", "сохранение ≥ 60 % фонда 1946–1991"],
  ["джентрификация берега", "соцквоты в земле, право возвращения"],
  ["«музей-забор»", "программирование мыса до проектирования"],
  ["партисипация для галочки", "официальный резерв проектов сообщества"],
];
s.addText(risks.map((r, j) => ({ text: r[0] + " → " + r[1], options: { bullet: bu(), breakLine: j < risks.length - 1 } })),
  { x: 7.0, y: 2.15, w: 5.8, h: 3.2, fontSize: 13.5, fontFace: F, color: TEXT, paraSpaceAfter: 10, margin: 0 });
s.addShape(pres.shapes.RECTANGLE, { x: M, y: 5.7, w: W - 2 * M, h: 0.9, fill: { color: "E8EEF4" } });
s.addText("Мониторинг: ежегодный публичный отчёт по целям Ц1–Ц4; все цифры воспроизводимы (scripts/check_numbers.py).",
  { x: M + 0.25, y: 5.85, w: W - 2 * M - 0.5, h: 0.6, fontSize: 14, fontFace: F, color: TEXT, valign: "middle", margin: 0 });

// ---------- 18 Финал ----------
s = pres.addSlide();
s.background = { color: PRIMARY };
s.addImage({ path: MAPS + "03_heritage.png", x: 0, y: 0, w: W, h: H, sizing: { type: "cover", w: W, h: H },
  transparency: 55 });
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: H, fill: { color: PRIMARY, transparency: 25 } });
s.addText("Две реки — общий берег.", { x: M, y: 2.6, w: 12, h: 1.1, fontSize: 42, fontFace: F, bold: true,
  color: "FFFFFF", margin: 0 });
s.addText("Стратегия развития Малой Охты 2027–2035 · github.com/mfthesun/malaya-okhta-strategy",
  { x: M, y: 3.9, w: 12, h: 0.5, fontSize: 16, fontFace: F, color: LIGHT, margin: 0 });
s.addText("Все цифры воспроизводимы: notebooks/01–04 + scripts/check_numbers.py · Контент для Figma: presentations/slides.md",
  { x: M, y: 6.5, w: 12.2, h: 0.5, fontSize: 12, fontFace: F, color: LIGHT, margin: 0 });

pres.writeFile({ fileName: "malaya_okhta_strategy_draft.pptx" }).then(() => console.log("PPTX готов: malaya_okhta_strategy_draft.pptx"));
