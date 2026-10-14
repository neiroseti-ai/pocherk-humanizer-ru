#!/usr/bin/env python3
"""Самопроверка текста по скиллу pocherk (v5).

    python check.py --result out.txt [--source src.txt] [--draft draft.txt] [--material mat.txt]
                    [--feed posts/] [--feed-n 12] [--assemble] [--source-kind brief|news|dictation]
                    [--mode rewrite|edit|write] [--profile claude|gigachat|yandex|core]
                    [--genre post|guide|news|opinion] [--json]

Источники (SKILL v4, «Владелец фразы»):
  --source    источник фактов (бриф, новость, диктовка). Без --draft — как раньше: черновик (rewrite) или текст
              автора (edit); тогда A и B сверяются с ним, а E считает фразы М относительно него;
  --draft     черновик модели (rewrite): A и B сверяются с черновиком, но потерей считается только то, что есть
              в источнике или материале; снятое М черновика — чистка (E7), а не ошибка;
  --material  дословные сообщения автора (ответы на вопросы, диктовка): опора для фраз от его лица (E4);
  --assemble  сборка из слов автора (режим write): каждая строка материала есть в тексте (E5);
  --feed      папка последних постов: концовки и зачины подряд (G).

Блоки:
  A — факт-замок (нужен --source): числа (цифрой, словом, «десятилетняя», «полчаса», время суток «22:00» =
      «десять вечера»; сколько раз встречаются, единицы при них, «почти / около / более» при числе; нумерация
      «1.» в начале строки и «1️⃣» — не числа), даты и дни, имена (жёстко — только внутри выровненной пары фраз,
      иначе подсказка), отрицания (пропавшие и добавленные; «не ниже F50» — граница, не отрицание), модальность
      (долженствование, возможность: «позволит сократить» ≠ «сократит», запрет, совет), вид и время глаголов
      (жёстко — только внутри выровненной пары фраз; «чтобы настроил» — наклонение, не время), пункты перечней
      (число пунктов — у списков с тем же содержанием), «а не», длина 85–115%, рамки мнения и источники (A11),
      цитаты в кавычках дословно (A12); знаменательные слова < 75% — подсказка, не нарушение;
  B — след ИИ-правки (нужен --source; markdown снят с обеих сторон): глиф тире, кавычки, «ё» (смешанную можно
      привести к конвенции большинства), двоеточия (все — с допуском +1 на 300 слов, раскрытия и ярлыки — без
      допуска), ярлык, ставший короткой фразой («Суть простая.»), «;», «— и», новое тире на месте двоеточия или
      оборота, лексический след правки, рамки мнения, источники и «честно», рамка, приклеенная через «, и,»,
      «, и / , а» (+1 на 200 слов), склейка двух фраз запятой, больше двух сочинительных союзов во фразе,
      «потому что» и «так что» (+1 на 300 слов), «X в том, что» (+1), «во-первых», «уверен / понял / сказали /
      признаюсь, что» (+1), средняя фраза короче исходника больше чем на 10% (rewrite — жёстко, edit — мягко),
      потерянные частицы, «надо», «потому что», длинные фразы, скобки, однофразные абзацы (без заголовков)…;
  C — бюджеты маркеров профиля по жанру и длине (budgets.json, собран из markers.json); рамки позиции (CORE-06) —
      не больше одной на абзац, в колонке и в тексте от первого лица не ограничиваются;
  D — ритм: длинные фразы, средняя длина фразы в окне жанра, разброс длин фраз;
  E — провенанс (v4): доля слов из источника и материала по фразам, фразы М, последняя фраза М (E1), числа и
      имена не из источника (E2), оценочные слова не из источника (E3), фраза от лица автора без опоры в
      материале (E4), сборка: строка материала не найдена в тексте (E5, v5 — жёстко; доля биграмм автора и фразы
      М — справка), «робкая правка» — меньше 5% изменённых слов при находках E и F (E6), снятое М (E7, справка);
      v5 (rewrite, черновик в --source или --draft): метки фраз черновика М / А? / вопрос / след (E13, справка),
      снята концовка или вопрос с содержанием (E8, жёстко; в середине текста — подсказка), следы площадки —
      хэштеги, @-подписи, ссылки, «заранее спасибо» (E9, жёстко, и в edit), снято действие или совет (E10,
      жёстко), сняты оценки черновика без источника (E11, подсказка), пропали глаголы сохранённых фраз (E12,
      справка). Без источника длина (A9): не короче 90% черновика без рамки модели и не длиннее 115%;
  F — подача (v4): концовка-мораль, призыв, благодарность, пожелание, вопрос читателю (F1; v5: у gigachat — только
      формулы и «Теперь …» в последней фразе, без источника концовка с содержанием — справка «А?»), связки-анонсы (F2),
      лишнее пояснение (F3), рамка промо (F4), заглушки (F5, жёстко), подзаголовки и строка-заголовок в посте
      (F6), шаблоны gigachat и yandex (F7);
  G — лента (v4, нужен --feed): третья концовка подряд того же типа (G1), зачины (G2, подсказка).

Жёсткость флагов E1, E3, F1, F4 задана замером точности на TEST (budgets.json → detectors, REVIEW.md v4):
жёсткий — только при точности не ниже 0,7. Флаги v5 E8 (концовка и вопрос), E9, E10 и предел длины без источника
жёсткие по правилу раунда 2 (bench/round2/RESULT.md §13), а не по замеру точности: на 60 пунктах раунда 2 они
сработали у v4 на 27 текстах (из них 18 из 20 пар, где v4 потерял пункт брифа) и у v3 на одном (REVIEW.md, v5).
Бюджеты C: страты «жанр × профиль» (budgets.json → strata);
маркеры, которые в правке (условие C корпуса) вдвое слабее, чем в тексте по брифу (A), только мягкие.

Код выхода 0: жёстких нарушений (A, B, C, E, F) нет, мягких в счёт (B в режиме edit, C, D, E, F, G) вместе не
больше одного. Иначе 1. Ошибка запуска — 2.
"""
from __future__ import annotations

import argparse
import difflib
import json
import math
import re
import statistics
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import textkit as tk  # noqa: E402

BUDGETS = json.loads((HERE / "budgets.json").read_text(encoding="utf-8"))
GENRES = ("post", "guide", "news", "opinion")
GENRE_RU = {"post": "пост", "guide": "гайд", "news": "новость", "opinion": "колонка"}
PROFILES = ("claude", "gigachat", "yandex", "core")
MODES = ("rewrite", "edit", "write")
MAX_FRAGS = 4


# =============================================================================== находки
@dataclass
class Frag:
    where: str          # «результат» / «исходник»
    text: str           # фраза или строка целиком
    match: str = ""     # что именно сработало


@dataclass
class Finding:
    block: str
    code: str
    title: str
    severity: str               # hard / soft / note
    message: str
    frags: list = field(default_factory=list)
    hint: str = ""
    counted: bool = True        # идёт ли в счёт кода выхода


def trim(s: str, n: int = 200) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def _fr(where, text, match=""):
    return Frag(where, trim(text), trim(match, 80))


@dataclass
class Hit:
    text: str
    match: str = ""


# =============================================================================== регулярки
_RX_CACHE: dict = {}


def rx(p: str) -> re.Pattern:
    r = _RX_CACHE.get(p)
    if r is None:
        r = _RX_CACHE[p] = re.compile(p, re.I | re.M | re.U)
    return r


def regex_hits(doc: tk.Doc, scope: str, pattern: str) -> list[Hit]:
    r = rx(pattern)
    out = []
    if scope == "sentence":
        for s in doc.sents:
            out += [Hit(s.raw, m.group(0)) for m in r.finditer(s.norm.strip())]
    elif scope == "line":
        for raw, norm in doc.lines:
            out += [Hit(raw, m.group(0)) for m in r.finditer(norm.strip())]
    elif scope == "first_sentence":
        if doc.sents:
            s = doc.sents[0]
            out += [Hit(s.raw, m.group(0)) for m in r.finditer(s.norm.strip())]
    elif scope == "last2_paras":
        for i in doc.last_paras_sents(2):
            s = doc.sents[i]
            out += [Hit(s.raw, m.group(0)) for m in r.finditer(s.norm.strip())]
    elif scope == "text":
        for m in r.finditer(doc.norm):
            out.append(Hit(m.group(0), m.group(0)))
    return out


# --------------------------------------------------------------- двоеточия
SERVICE_LABELS = frozenset(
    "цена цены стоимость шаг этап фото источник источники адрес дата даты время место автор ссылка ссылки телефон "
    "контакты сайт вход формат срок сроки платформы платформа требования размер вес состав ингредиенты вопрос "
    "ответ ps upd обновление часы город страна жанр режиссер версия лицензия язык цель итого характеристики "
    "параметры комплектация расписание программа участники спикеры примечание".split())
COLON_REVEAL_FORM = r"\b(?:прост|простой|простая|такая|такой|так)\s*:|\bя (?:уверен|уверена|убежден|убеждена)\s*:"
_INTRO_WORDS = frozenset("конечно например кстати впрочем наверное итак правда кажется видимо разумеется возможно "
                         "пожалуй да нет ну вот во-первых во-вторых в-третьих".split())


def _wordlist(s: str) -> list[str]:
    return re.findall(r"[^\W_]+(?:-[^\W_]+)*", s)


def _is_inline_list(after: str) -> bool:
    items = _enum_items(after)
    return len(items) >= 3


_CLAUSE_START = frozenset("и а но или если что чтобы когда где куда откуда который которая которое которые которых "
                          "потому поэтому так как хотя пока будто словно ибо зато то чем насколько".split())
_PERS_NOMN = frozenset("я мы ты вы он она оно они".split())


def _clause_like(wl: list[str]) -> bool:
    """Кусок похож на придаточное или сказуемое, а не на пункт перечня
    («мы не правы», «насколько мне известно», «лучше сосредоточиться на цифрах»)."""
    if not wl:
        return True
    if wl[0].lower() in _CLAUSE_START and len(wl) > 1 and wl[0].lower() not in ("и", "или"):
        return True
    if not tk.has_morph():
        return False
    ps = [tk.parse(w.lower()) for w in wl]
    if any(p is not None and p.pos in ("VERB", "GRND", "PRED", "ADJS", "PRTS") for p in ps):
        return True
    if any(p is not None and p.pos == "ADVB" and "Prdx" in p.tags for p in ps) and len(wl) > 1:
        return True
    if any(w.lower() in _PERS_NOMN for w in wl):
        return True
    if any(p is not None and p.pos == "COMP" for p in ps) and any(p is not None and p.pos == "INFN" for p in ps):
        return True
    if ps[0] is not None and ps[0].pos in ("PRTF", "PRTS") and not any(p is not None and p.pos == "NOUN" for p in ps):
        return True
    return False


_LAST_PAIR_RX = re.compile(r"^(.+?)\s+(?:и|или|а также)\s+(.+)$")


def _enum_items(seg: str) -> list[str]:
    """Пункты перечисления через запятую в куске фразы (каждый ≤ 4 слов, последний может быть «X и Y»,
    где X и Y — тоже по ≤ 4 слова: «звук, свет, зарядку телефона и стабильность интернета»)."""
    parts = [p.strip() for p in re.split(r",(?![^()]*\))", seg)]
    best: list[str] = []
    run: list[str] = []

    def close(items: list[str]):
        nonlocal best
        if len(items) >= 3 and len(items) > len(best):
            best = items

    def split_last(r: list[str]) -> list[str]:
        m = _LAST_PAIR_RX.match(r[-1])
        return r[:-1] + ([m.group(1), m.group(2)] if m and len(r) >= 2 else [r[-1]])

    for p in parts + [None]:
        if p is not None:
            wl = _wordlist(p)
            ok = (1 <= len(wl) <= 4 and not (len(wl) == 1 and wl[0].lower() in _INTRO_WORDS)
                  and not _clause_like([w for w in wl if w.lower() not in ("и", "или")] if run else wl))
            if not ok and not run and len(wl) <= 7 and wl and wl[0].lower() not in _CLAUSE_START:
                # первый кусок может быть длиннее: «Мы купили хлеб, молоко и сыр»
                # (но не вводное или придаточное: «Насколько мне известно, …», «Если …, …»)
                run = [p]
                continue
            if not ok and run:
                # последний кусок «X и Y» длиннее 4 слов, но X и Y — короткие пункты
                m = _LAST_PAIR_RX.match(p)
                if m:
                    halves = [_wordlist(x) for x in m.groups()]
                    if all(1 <= len(h) <= 4 and not _clause_like(h) for h in halves):
                        close(run + [m.group(1), m.group(2)])
                        run = []
                        continue
        else:
            ok = False
        if ok:
            run.append(p)
            continue
        if run:
            close(split_last(run))
        run = []
        if p is not None:
            wl = _wordlist(p)
            if len(wl) <= 7 and wl and wl[0].lower() not in _CLAUSE_START:
                run = [p]
    return best


def colon_kinds(sent: tk.Sent) -> list[tuple[str, str]]:
    """Функция каждого «:» во фразе: time / end / speech / service / label / list / reveal."""
    s = sent.norm.strip()
    out = []
    first = True
    for m in re.finditer(r":", s):
        i = m.start()
        before, after = s[:i], s[i + 1:]
        frag = (before[-40:] + ":" + after[:40]).strip()
        if before.count('"') % 2 == 1:
            first = False
            continue                                   # «:» внутри цитаты — не голос автора
        if re.search(r"\d\s*$", before) and re.match(r"\s*\d", after):
            out.append(("time", frag))
            continue
        if re.search(r"(?:https?|ftp)$", before, re.I):
            continue
        if re.match(r"-?[()DdPpРрОоЗз3]{1,}(?:\W|$)", after) and not re.match(r"\s", after):
            continue                                   # смайлик «:)», «:-(», «:D»
        if not after.strip() or re.fullmatch(r"\s*[\d.,)]{1,6}\s*\.?\s*", after):
            out.append(("end", frag))                  # перед списком или «аппарат: 2.» (ссылка на фото)
            first = False
            continue
        if re.match(r'\s*["—\'«]', after) or re.match(r"\s*-\s", after):
            out.append(("speech", frag))
            first = False
            continue
        bw = _wordlist(before)
        lead = re.match(r'^[\s"(\'—-]*', before).end()
        is_label_shape = first and 1 <= len(bw) <= 3 and "," not in before and lead <= len(before)
        first = False
        if is_label_shape and (any(tk.fold_yo(w.lower()) in SERVICE_LABELS for w in bw)
                               or any(ch.isdigit() for ch in before)):
            out.append(("service", frag))
            continue
        if _is_inline_list(after.split(":", 1)[0]):     # перечень сразу за этим «:», а не за следующим
            out.append(("list", frag))                 # двоеточие перед перечнем (NT-15)
            continue
        if is_label_shape and not rx(COLON_REVEAL_FORM).search(before + ":"):
            has_pred = False
            if tk.has_morph():
                has_pred = any(tk.is_predicate(tk.parse(w.lower())) for w in bw)
            if not has_pred:
                out.append(("label", frag))
                continue
        out.append(("reveal", frag))
    return out


def colon_hits(doc: tk.Doc, kinds: set[str]) -> list[Hit]:
    out = []
    for s in doc.sents:
        if ":" not in s.norm:
            continue
        for k, frag in colon_kinds(s):
            if k in kinds:
                out.append(Hit(s.raw, frag))
    return out


# --------------------------------------------------------------- прочие методы
_YO_FALLBACK = frozenset("еще ее нее свое мое твое идет придет пойдет найдет ведет дает берет живет ждет зовет "
                         "растет несет везет жжет плывет врет кладет".split())


def yo_hits(doc: tk.Doc) -> tuple[list[Hit], list[Hit]]:
    """Слова, которые однозначно требуют «ё»: (написаны с «ё», написаны через «е»)."""
    with_yo, without = [], []
    for s in doc.sents:
        for t in s.words:
            if tk.has_morph():
                if not (t.w and t.w.yo_word):
                    continue
            elif t.low not in _YO_FALLBACK:
                continue
            (with_yo if "ё" in t.text.lower() else without).append(Hit(s.raw, t.text))
    return with_yo, without


def markdown_hits(doc: tk.Doc) -> list[Hit]:
    out = []
    for raw, _ in doc.lines:
        for m in re.finditer(r"^\s*#{1,6}\s+\S.*$|\*\*[^*\n]+\*\*|__[^_\n]+__", raw):
            out.append(Hit(raw, m.group(0)))
    return out


def structure_hits(doc: tk.Doc) -> list[Hit]:
    out = markdown_hits(doc)
    for raw, norm in doc.lines:
        if re.match(r"^\s*(?:[-*•▪●◦]|\d{1,2}[.)])\s+\S", raw) or re.match(r"^\s*шаг\s+\d", norm, re.I):
            out.append(Hit(raw, raw.strip()[:30]))
    return out


def count_counter(c: dict, doc: tk.Doc) -> list[Hit]:
    m = c["method"]
    if m == "regex":
        return regex_hits(doc, c["scope"], c["regex"])
    if m == "raw_regex":
        out = []
        for mm in rx(c["regex"]).finditer(doc.text):
            i = doc.sent_at(mm.start())
            out.append(Hit(doc.sents[i].raw if i is not None else doc.text[max(0, mm.start() - 40):mm.end() + 40],
                           mm.group(0)))
        return out
    if m == "colon_label":
        return colon_hits(doc, {"label"})
    if m == "colon_reveal":
        return colon_hits(doc, {"reveal"})
    if m == "colon_all":
        return colon_hits(doc, {"label", "reveal", "list", "speech", "service"})
    if m == "dash_tail":
        return [Hit(s.raw, f) for s in doc.sents for f in tk.dash_tail_hits(s)]
    if m == "dash_prose":
        out = []
        for s in doc.sents:
            if "—" not in s.norm:
                continue
            classes = tk.classify_dash_sentence(s.norm, s.line_start)
            pos = [mm.start() for mm in re.finditer("—", s.norm)]
            for p, cl in zip(pos, classes):
                if cl not in tk.NON_PROSE_DASH:
                    out.append(Hit(s.raw, s.norm[max(0, p - 25):p + 25].strip()))
        return out
    if m == "rubric":
        return [Hit(doc.sents[i].raw + " " + doc.sents[i + 1].raw, doc.sents[i].raw)
                for i in range(len(doc.sents) - 1) if tk.is_rubric_period(doc, i)]
    if m == "trailing_gerund":
        return [Hit(s.raw, "") for s in doc.sents if tk.trailing_gerund(s)]
    if m == "gen_chain":
        return [Hit(s.raw, "") for s in doc.sents for _ in range(tk.gen_chains(s))]
    if m == "yo_mixed":
        a, b = yo_hits(doc)
        if a and b:
            minority = a if len(a) <= len(b) else b
            return [minority[0]] if minority else []
        return []
    if m == "excl":
        return [Hit(s.raw, "!") for s in doc.sents for _ in range(s.norm.count("!"))]
    if m == "emoji":
        out = []
        for raw, _ in doc.lines:
            out += [Hit(raw, e) for e in tk.EMOJI_RX.findall(raw)]
        return out
    if m == "markdown":
        return markdown_hits(doc)
    if m == "nominal_share":
        return []
    raise ValueError(f"неизвестный метод {m}")


# =============================================================================== бюджеты
def length_bin(n: int) -> int:
    lb = BUDGETS["length_bins"]
    return 0 if n <= lb["short_max"] else 1 if n <= lb["mid_max"] else 2


def length_label(n: int) -> str:
    return BUDGETS["length_bins"]["labels"][length_bin(n)]


def allowed(b: dict, doc: tk.Doc, genre: str) -> int | None:
    t = b["type"]
    n = doc.n_words
    if t == "fixed":
        return b["max"]
    if t == "by_len":
        return b["max"][length_bin(n)]
    if t == "by_genre":
        return b["max"][genre]
    if t == "per_words":
        v = max(b["min"], n // b["per"])
        gm = (b.get("genre_min") or {}).get(genre)
        return max(v, gm) if gm else v
    if t == "per_sents":
        return max(b["min"], doc.n_sents // b["per"])
    if t == "density":
        return max(b["min"], round(b["per1000"][genre] * n / 1000))
    if t == "per_para":
        return b["max"]
    if t == "note":
        return None
    raise ValueError(t)


def applies(c: dict, profile: str, genre: str) -> bool:
    if c.get("genres") and genre not in c["genres"]:
        return False
    if profile == "core":
        return "core" in c["profiles"]
    return "core" in c["profiles"] or profile in c["profiles"]


FP_RX = r"\b(?:я|меня|мне|мной|мною|мой|моя|мое|мои|моего|моей|моему|моим|моими|моих|мою|моем)\b"


def first_person_count(doc: tk.Doc) -> int:
    """«я / мне / мой» и глаголы 1-го лица ед. ч. вне рамок мнения: сами рамки («я считаю») не делают текст личным."""
    n = 0
    for s in doc.sents:
        t = _mask(_mask(s.norm, rx(PERSONA_RX)), rx(OPINION_STRICT))
        n += len(rx(FP_RX).findall(t))
        if tk.has_morph():
            for w in re.findall(r"[^\W\d_]+", t):
                p = tk.parse(w.lower())
                if p is not None and p.pos == "VERB" and "1per" in p.tags and "sing" in p.tags:
                    n += 1
    return n


def is_first_person(doc: tk.Doc) -> bool:
    """Текст от первого лица: не меньше 3 «я»-слов вне рамок и не реже одного на 100 слов."""
    n = first_person_count(doc)
    return n >= 3 and n * 100 >= doc.n_words


def para_groups(doc: tk.Doc) -> list[list[int]]:
    """Абзацы (куски между пустыми строками); в тексте без пустых строк — строки."""
    if doc.has_paragraphs:
        return doc.paras
    by_line: dict[int, list[int]] = {}
    for i, s in enumerate(doc.sents):
        by_line.setdefault(s.line, []).append(i)
    return list(by_line.values())


def _over_per_para(c: dict, doc: tk.Doc) -> list[list[Hit]]:
    r = rx(c["regex"])
    out = []
    for p in para_groups(doc):
        hs = [Hit(doc.sents[i].raw, m.group(0)) for i in p for m in r.finditer(doc.sents[i].norm.strip())]
        if len(hs) > c["budget"]["max"]:
            out.append(hs)
    return out


def _per_para_finding(c: dict, res: tk.Doc, genre: str, mode: str, src: tk.Doc | None) -> list[Finding]:
    """Бюджет на абзац (CORE-06: рамки позиции подряд). В колонке и в тексте от первого лица не применяется:
    там рамки — голос автора, а снятая рамка превращает мнение в факт (DEV-замер, P1)."""
    b = c["budget"]
    over = _over_per_para(c, res)
    if not over:
        return []
    frs = [_fr("результат", h.text, h.match) for hs in over for h in hs][:MAX_FRAGS]
    exempt = ("колонка" if genre in b.get("skip_genres", []) else
              "текст от первого лица" if b.get("skip_first_person") and is_first_person(res) else None)
    msg = f"абзацев, где рамок больше {b['max']}: {len(over)} (рамок в них {sum(len(h) for h in over)})"
    if exempt:
        return [Finding("C", c["marker"], c["title"], "note",
                        f"{msg}; {exempt}: бюджет не применяется, рамки автора не снимать", frs, counted=False)]
    if mode == "edit" and src is not None and len(_over_per_para(c, src)) >= len(over):
        return [Finding("C", c["marker"], c["title"], "note", f"{msg}, в исходнике так же: почерк автора",
                        hint="В режиме edit не трогать.", counted=False)]
    return [Finding("C", c["marker"], c["title"], "soft", f"{msg}; бюджет — {b['max']} на абзац ({c['budget_text']})",
                    frs, c["hint"])]


def stratum(c: dict, profile: str, genre: str) -> dict:
    """Страта «жанр × профиль» из budgets.json (build_budgets.py ← bench/round2/b2/strata.json)."""
    return ((BUDGETS.get("strata") or {}).get(c["key"]) or {}).get(profile) or {}


def _short_override(c: dict, profile: str, genre: str, doc: tk.Doc) -> dict | None:
    """Особые бюджеты страты: тире у GigaChat в коротких постах — до частоты людей жанра (SKILL v4, шаг 4)."""
    for o in (BUDGETS.get("strata_overrides") or []):
        if (o["key"] == c["key"] and profile in o["profiles"] and genre in o["genres"]
                and doc.n_words <= o["max_words"]):
            return o
    return None


def block_c(res: tk.Doc, genre: str, profile: str, mode: str, src: tk.Doc | None,
            excl_ref: tk.Doc | None = None) -> tuple[list[Finding], list[str]]:
    """excl_ref (v4) — источник фактов или материал: «!» — 0, если их нет у автора или в источнике, иначе 1."""
    out: list[Finding] = []
    skipped = []
    for c in BUDGETS["counters"]:
        override = _short_override(c, profile, genre, res)
        if c["key"] == "excl" and excl_ref is not None:
            pass                                     # «!» с привязкой к источнику — в любом профиле
        elif not applies(c, profile, genre) and override is None:
            continue
        if c.get("needs_morph") and not tk.has_morph():
            skipped.append(f"{c['marker']} {c['title']}")
            continue
        if c["budget"]["type"] == "per_para":
            out += _per_para_finding(c, res, genre, mode, src)
            continue
        code = c["marker"]
        if c["method"] == "nominal_share":
            v = tk.nominal_share(res)
            thr = c["budget"]["threshold"]
            if v is not None and v > thr and res.n_words >= 100:
                out.append(Finding("C", code, c["title"], "note",
                                   f"доля отглагольных существительных {v:.2f} (медиана людей {thr:.2f})",
                                   hint=c["hint"], counted=False))
            continue
        hits = count_counter(c, res)
        if c["key"] == "wrapper":                   # заглушки считает F5 (жёстко), здесь — только обёртка
            hits = [h for h in hits if not PLACEHOLDER_RX.search(h.match)]
        lim = allowed(c["budget"], res, genre)
        budget_text = c["budget_text"]
        if override is not None and not applies(c, profile, genre):
            lim = max(override["min"], round(override["per1000"] * res.n_words / 1000))
            budget_text = override["budget_text"]
        if c["key"] == "excl" and excl_ref is not None:
            ref_excl = excl_ref.norm.count("!")
            lim = 0 if ref_excl == 0 else min(lim if lim is not None else 1, 1)
            budget_text = ("0: в источнике и у автора «!» нет" if ref_excl == 0
                           else "не больше 1: «!» есть в источнике или у автора")
        n = len(hits)
        if lim is None:
            if hits:
                out.append(Finding("C", code, c["title"], "note", f"{n} — проверь, есть ли за каждой оценкой факт",
                                   [_fr("результат", h.text, h.match) for h in hits[:MAX_FRAGS]], c["hint"], False))
            continue
        if c["method"] == "dash_prose":
            floor = c["budget"].get("floor_per1000", {}).get(genre)
            dens = n * 1000 / res.n_words if res.n_words else 0
            if floor and src is not None and mode != "write" and res.n_words >= 150:
                src_n = len(count_counter(c, src))
                src_d = src_n * 1000 / src.n_words if src.n_words else 0
                if dens < floor <= src_d:
                    out.append(Finding("C", code, "Тире вычищены ниже медианы жанра", "note",
                                       f"{dens:.1f} на 1000 слов при медиане людей {floor} (в исходнике {src_d:.1f})",
                                       hint="Грамматическое тире не трогать; сокращать только повороты и хвосты.",
                                       counted=False))
        if n <= lim:
            continue
        if c["budget"].get("counted") is False:
            out.append(Finding("C", code, c["title"], "note", f"{n} при ориентире {lim}: {c['budget']['why_not_counted']}",
                               [_fr("результат", h.text, h.match) for h in hits[:MAX_FRAGS]], c["hint"], False))
            continue
        unit = ""
        if c["method"] == "dash_prose":
            unit = f" ({n * 1000 / max(res.n_words, 1):.1f} на 1000 слов)"
        msg = f"{n}{unit} при бюджете {lim} ({budget_text})"
        if mode == "edit" and src is not None:
            src_n = len(count_counter(c, src))
            if n <= src_n:
                out.append(Finding("C", code, c["title"], "note", f"{n} при бюджете {lim}, но в исходнике было {src_n}: "
                                   "почерк автора, правка не добавила", hint="В режиме edit не трогать.", counted=False))
                continue
            msg += f"; в исходнике было {src_n}"
        st = stratum(c, profile, genre)
        sev = "hard" if (st.get("severity") == "hard" and override is None) else "soft"
        if sev == "hard":
            msg += f"; жёстко в профиле {profile}: {st.get('why', '')}"
        out.append(Finding("C", code, c["title"], sev, msg,
                           [_fr("результат", h.text, h.match) for h in hits[:MAX_FRAGS]], c["hint"]))
    # один маркер — не больше одного мягкого нарушения в счёт (ярлык и все «:», шесть книжных связок…)
    seen = set()
    for f in out:
        if f.severity == "soft" and f.counted:
            if f.code in seen:
                f.counted = False
                f.message += " — тот же маркер, в счёт не идёт"
            seen.add(f.code)
    return out, skipped


# =============================================================================== D: ритм
@dataclass
class Rhythm:
    n_sents: int
    n_words: int
    n_long: int
    mean: float | None
    cv: float | None
    longest: int
    para_cv: float | None


def rhythm(doc: tk.Doc) -> Rhythm:
    lw = BUDGETS["rhythm"]["long_words"]
    lens = [s.n_words for s in doc.sents if s.n_words > 0]
    n = len(lens)
    mean = sum(lens) / n if n else None
    cv = (statistics.pstdev(lens) / mean) if n >= 2 and mean else None
    para_cv = None
    if doc.has_paragraphs and len(doc.paras) >= 2:
        pl = [sum(doc.sents[i].n_words for i in p) for p in doc.paras]
        pm = sum(pl) / len(pl)
        para_cv = statistics.pstdev(pl) / pm if pm else None
    return Rhythm(n, doc.n_words, sum(1 for x in lens if x > lw), mean, cv, max(lens) if lens else 0, para_cv)


def _d_checks(r: Rhythm, genre: str) -> dict:
    cfg = BUDGETS["rhythm"]
    res = {}
    # CORE-01: «текст от 150 слов» — все три нормы ритма; плюс ≥ 8 фраз (self_check.rhythm)
    if r.n_sents >= cfg["min_sents"] and r.n_words >= cfg["long_min_words"]:
        need = max(1, r.n_words // cfg["long_per_words"])
        res["long"] = (r.n_long < need, need)
        lo, hi = cfg["mean_window"][genre]
        res["mean_lo"] = (r.mean is not None and r.mean < lo, lo)
        res["mean_hi"] = (r.mean is not None and r.mean > hi, hi)
        if genre not in cfg["cv_skip_genres"] and r.n_sents >= cfg["cv_min_sents"]:
            res["cv"] = (r.cv is not None and r.cv < cfg["cv_min"], cfg["cv_min"])
    if r.para_cv is not None:
        res["para_cv"] = (r.para_cv < cfg["para_cv_min"], cfg["para_cv_min"])
    return res


def block_d(res: tk.Doc, genre: str, mode: str, src: tk.Doc | None) -> list[Finding]:
    cfg = BUDGETS["rhythm"]
    r = rhythm(res)
    chk = _d_checks(r, genre)
    rs = rhythm(src) if src is not None else None
    sc = _d_checks(rs, genre) if rs is not None else {}
    out = []

    def same_in_source(key: str) -> bool:
        return mode == "edit" and src is not None and sc.get(key, (False,))[0]

    long_lw = cfg["long_words"]
    counted_any = False
    if chk.get("long", (False,))[0]:
        need = chk["long"][1]
        longest = sorted(res.sents, key=lambda s: -s.n_words)[:2]
        f = Finding("D", "CORE-01", "Нет длинных фраз", "soft",
                    f"фраз длиннее {long_lw} слов: {r.n_long}, нужно не меньше {need} "
                    f"(по одной на 150–200 слов; всего {r.n_words} слов, {r.n_sents} фраз); самая длинная — {r.longest} слов",
                    [_fr("результат", s.raw, f"{s.n_words} слов") for s in longest],
                    "Склеивать только связанные по смыслу фразы, лучше подчинением: «который», «когда», «если», "
                    "«чтобы», причастный или деепричастный оборот. «, и» / «, а» — не чаще раза на 200 слов, во фразе "
                    "не больше двух сочинительных союзов, две самостоятельные фразы не через запятую. Не через тире "
                    "и двоеточие; «потому что» — только если причина есть в исходнике. Нечего склеить естественно — "
                    "не склеивать.")
        if same_in_source("long") and rs is not None and r.n_long >= rs.n_long:
            f.severity, f.counted = "note", False
            f.message += f" (в исходнике тоже {rs.n_long}: почерк автора)"
        out.append(f)
        counted_any = counted_any or f.counted
    if chk.get("mean_lo", (False,))[0]:
        lo, hi = cfg["mean_window"][genre]
        f = Finding("D", "CORE-01", "Средняя фраза короче окна жанра", "soft",
                    f"средняя длина фразы {r.mean:.1f} слова, окно жанра «{GENRE_RU[genre]}» {lo}–{hi}",
                    hint="Не дробить; склеивать соседние короткие фразы об одном предмете.")
        if counted_any:
            f.severity, f.counted = "note", False
            f.message += " (та же причина, что и выше; в счёт не идёт)"
        elif same_in_source("mean_lo"):
            f.severity, f.counted = "note", False
            f.message += " (в исходнике так же)"
        out.append(f)
        counted_any = counted_any or f.counted
    if chk.get("mean_hi", (False,))[0]:
        lo, hi = cfg["mean_window"][genre]
        out.append(Finding("D", "CORE-01", "Средняя фраза длиннее окна жанра", "note",
                           f"средняя длина фразы {r.mean:.1f} слова при окне {lo}–{hi}: допустимо, если так пишет автор; "
                           "не склеивай дальше", counted=False))
    if chk.get("cv", (False,))[0]:
        f = Finding("D", "CORE-01", "Фразы одной длины (метроном)", "soft",
                    f"разброс длин фраз CV {r.cv:.2f}, нужно не меньше {cfg['cv_min']}",
                    hint="Рядом с длинной фразой допустима короткая; не выравнивать фразы по длине.")
        if counted_any:
            f.severity, f.counted = "note", False
            f.message += " (та же причина; в счёт не идёт)"
        elif same_in_source("cv"):
            f.severity, f.counted = "note", False
            f.message += " (в исходнике так же)"
        out.append(f)
    if (genre in cfg["cv_skip_genres"] and r.n_sents >= cfg["cv_min_sents"] and r.n_words >= cfg["long_min_words"]
            and r.cv is not None and r.cv < cfg["cv_min"]):
        out.append(Finding("D", "CORE-01", "Разброс длин фраз", "note",
                           f"CV {r.cv:.2f}; для новостей порог не применяется ({cfg['cv_skip_note']})", counted=False))
    if chk.get("para_cv", (False,))[0]:
        out.append(Finding("D", "CORE-02", "Абзацы одной длины", "note",
                           f"разброс длин абзацев CV {r.para_cv:.2f} (ориентир ≥ {cfg['para_cv_min']}); "
                           "у 40% людей тоже ниже — подсказка, не нарушение",
                           hint="В ИИ-черновике допустимы рядом однофразный и длинный абзац; в чужом тексте абзацы не склеивать.",
                           counted=False))
    return out


# =============================================================================== A: факт-замок
NUM_LEMMAS = {
    "ноль": 0, "нуль": 0, "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7,
    "восемь": 8, "девять": 9, "десять": 10, "одиннадцать": 11, "двенадцать": 12, "тринадцать": 13,
    "четырнадцать": 14, "пятнадцать": 15, "шестнадцать": 16, "семнадцать": 17, "восемнадцать": 18,
    "девятнадцать": 19, "двадцать": 20, "тридцать": 30, "сорок": 40, "пятьдесят": 50, "шестьдесят": 60,
    "семьдесят": 70, "восемьдесят": 80, "девяносто": 90, "сто": 100, "двести": 200, "триста": 300,
    "четыреста": 400, "пятьсот": 500, "шестьсот": 600, "семьсот": 700, "восемьсот": 800, "девятьсот": 900,
    "тысяча": 1000, "миллион": 10 ** 6, "миллиард": 10 ** 9, "полтора": 1.5, "двое": 2, "трое": 3,
    "четверо": 4, "пятеро": 5, "шестеро": 6, "семеро": 7,
}
_NUM_FALLBACK = [
    (0, r"ноль|нуль|ноля|нуля|нолем|нулем"), (1, r"один|одна|одно|одного|одной|одному|одним|одном|одну"),
    (2, r"два|две|двух|двум|двумя|двое|двоих"), (3, r"три|трех|трем|тремя|трое|троих"),
    (4, r"четыре|четырех|четырем|четырьмя|четверо"), (5, r"пять|пяти|пятью|пятеро"),
    (6, r"шесть|шести|шестью"), (7, r"семь|семи"), (8, r"восемь|восьми|восемью"), (9, r"девять|девяти|девятью"),
    (10, r"десять|десяти|десятью"), (11, r"одиннадцат[ьи]"), (12, r"двенадцат[ьи]"), (13, r"тринадцат[ьи]"),
    (14, r"четырнадцат[ьи]"), (15, r"пятнадцат[ьи]"), (16, r"шестнадцат[ьи]"), (17, r"семнадцат[ьи]"),
    (18, r"восемнадцат[ьи]"), (19, r"девятнадцат[ьи]"), (20, r"двадцат[ьи]|двадцатью"), (30, r"тридцат[ьи]|тридцатью"),
    (40, r"сорок"), (50, r"пятьдесят|пятидесяти"), (60, r"шестьдесят|шестидесяти"), (70, r"семьдесят|семидесяти"),
    (80, r"восемьдесят|восьмидесяти"), (90, r"девяносто|девяноста"), (100, r"сто"),
    (200, r"двести|двухсот"), (300, r"триста|трехсот"), (400, r"четыреста|четырехсот"), (500, r"пятьсот|пятисот"),
    (1000, r"тысяч\w*"), (10 ** 6, r"миллион\w*"), (10 ** 9, r"миллиард\w*"), (1.5, r"полтора|полторы|полутора"),
]
_NUM_FALLBACK_RX = [(v, re.compile(rf"^(?:{p})$")) for v, p in _NUM_FALLBACK]
MULTIPLIERS = {1000, 10 ** 6, 10 ** 9}
MULT_ABBR = re.compile(r"^(?:тыс|млн|млрд|к|k|m)\.?$", re.I)


def _word_value(t: tk.Tok):
    if t.w is not None:
        if t.w.lemma in NUM_LEMMAS and (t.w.pos in ("NUMR", "NOUN") or t.w.lemma in ("тысяча", "миллион", "миллиард")):
            return NUM_LEMMAS[t.w.lemma]
        return None
    for v, r in _NUM_FALLBACK_RX:
        if r.match(t.low):
            return v
    return None


def _fmt(v) -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


_DATE_RX = re.compile(r"\b\d{1,2}\.\d{1,2}\.(?:\d{4}|\d{2})\b")
_NUM_RX = re.compile(r"(?<![\d])(\d{1,3}(?: \d{3})+(?![\d])|\d+)(?:[.,](\d+)(?![\d]))?")

# --- время: «5:00» = «пять утра», «22:00» = «десять вечера», «22:50» ≈ «без десяти одиннадцать»
_HOUR_WORDS = {
    1: r"час|одного|один", 2: r"двух|два", 3: r"трех|три", 4: r"четырех|четыре", 5: r"пяти|пять", 6: r"шести|шесть",
    7: r"семи|семь", 8: r"восьми|восемь", 9: r"девяти|девять", 10: r"десяти|десять", 11: r"одиннадцати|одиннадцать",
    12: r"двенадцати|двенадцать"}
_HOUR_ORD = {1: "первого", 2: "второго", 3: "третьего", 4: "четвертого", 5: "пятого", 6: "шестого", 7: "седьмого",
             8: "восьмого", 9: "девятого", 10: "десятого", 11: "одиннадцатого", 12: "двенадцатого"}
_MIN_WORDS = {5: r"пяти", 10: r"десяти", 15: r"пятнадцати|четверти", 20: r"двадцати", 25: r"двадцати пяти"}
_HOUR_ALT = "|".join(p for _, p in sorted(_HOUR_WORDS.items(), key=lambda kv: -len(kv[1])))
_DAYPART_RX = r"(утра|дня|вечера|ночи)"
_TIME_DIGITAL_RX = re.compile(r"(?<![\d:])([01]?\d|2[0-3]):([0-5]\d)(?![\d:])")
# «пять утра», «в 10 вечера», «два часа дня», «в три ночи»; «3 дня» и «две ночи» без «час» — это сутки, не время
_TIME_DAYPART_RX = re.compile(
    rf"\b(\d{{1,2}}|{_HOUR_ALT})\s+(?:(?:час(?:а|ов)?|ч\.?)\s+{_DAYPART_RX}|(утра|вечера))\b"
    rf"|\bв\s+(\d{{1,2}}|{_HOUR_ALT})\s+(ночи)\b|\b(час)\s+(дня)\b", re.I)
_TIME_BEZ_RX = re.compile(
    rf"\bбез\s+(\d{{1,2}}|{'|'.join(sorted((p for p in _MIN_WORDS.values()), key=len, reverse=True))})"
    rf"(?:\s+минут\w*)?\s+(\d{{1,2}}|{_HOUR_ALT})\b(?:\s+{_DAYPART_RX}\b)?", re.I)
_TIME_HALF_RX = re.compile(rf"\b(?:в\s+половине|половина|пол)\s+({'|'.join(_HOUR_ORD.values())})\b"
                           rf"(?:\s+{_DAYPART_RX}\b)?", re.I)
_TIME_NOON_RX = re.compile(r"\b(полдень|полночь)\b", re.I)
# «до 22.00 вечера», «засыпаю до 22.50»: время через точку — только с частью суток или после «с / до / в / к / около /
# после» при часе от 13 (иначе это дробь: «в 9.30» не трогаем)
_TIME_DOT_RX = re.compile(rf"(?:\b(с|до|в|к|около|после)\s+)?(?<![\d.,])([01]?\d|2[0-3])\.([0-5]\d)(?![\d.,]?\d)"
                          r"(?!\s*(?:руб|р\.|₽|долл|евро|€|\$|%|процент|тыс|млн|млрд|кг|км|см|мм|м\b|л\b|г\b|балл|раз))"
                          rf"(?:\s+{_DAYPART_RX}\b)?", re.I)


def _hour_value(s: str) -> int | None:
    s = s.lower()
    if s.isdigit():
        return int(s)
    for h, p in _HOUR_WORDS.items():
        if re.fullmatch(p, s):
            return h
    return None


def _daypart_hour(h: int, part: str | None) -> int | None:
    """Час в 24-часовом виде; None, если без части суток час неоднозначен (1–12)."""
    if part is None:
        return h if h > 12 or h == 0 else None
    part = part.lower()
    if part == "утра":
        return 0 if h == 12 else h
    if part in ("дня", "вечера"):
        return h if h >= 12 else h + 12
    return 0 if h == 12 else (h if h <= 5 else (h if h > 12 else h + 12))      # ночи


def _time_key(h: int, m: int, part: str | None = None) -> tuple[str, set]:
    """(ключ, равнозначные ключи): «22:50» точно; «~10:50» — 10:50 или 22:50."""
    h24 = _daypart_hour(h, part)
    if h24 is not None:
        return f"{h24}:{m:02d}", set()
    h12 = h % 12
    return f"~{h12}:{m:02d}", {f"{h12}:{m:02d}", f"{h12 + 12}:{m:02d}"}


def time_exprs(norm: str) -> list[tuple[int, int, str, set]]:
    """Выражения времени во фразе: (начало, конец, ключ, равнозначные ключи)."""
    out: list[tuple[int, int, str, set]] = []
    taken: list[tuple[int, int]] = []

    def add(m, h, mi, part=None):
        if any(a < m.end() and m.start() < b for a, b in taken):
            return
        if h is None or not (0 <= h <= 24) or not (0 <= mi < 60):
            return
        key, alts = _time_key(h % 24, mi, part)
        taken.append((m.start(), m.end()))
        out.append((m.start(), m.end(), key, alts))

    for m in _TIME_BEZ_RX.finditer(norm):
        mw = m.group(1).lower()
        mins = int(mw) if mw.isdigit() else next(v for v, p in _MIN_WORDS.items() if re.fullmatch(p, mw))
        h = _hour_value(m.group(2))
        if h is not None:
            add(m, (h - 1) % 12 or 12, 60 - mins, m.group(3))
    for m in _TIME_HALF_RX.finditer(norm):
        h = next(k for k, v in _HOUR_ORD.items() if v == m.group(1).lower())
        add(m, (h - 1) % 12 or 12, 30, m.group(2))
    for m in _TIME_DOT_RX.finditer(norm):
        h, mi, part = int(m.group(2)), int(m.group(3)), m.group(4)
        if part or (m.group(1) and h >= 13):
            add(m, h, mi, part)
    for m in _TIME_DAYPART_RX.finditer(norm):
        if m.group(1):
            add(m, _hour_value(m.group(1)), 0, m.group(2) or m.group(3))
        elif m.group(4):
            add(m, _hour_value(m.group(4)), 0, m.group(5))
        else:
            add(m, 1, 0, m.group(7))
    for m in _TIME_DIGITAL_RX.finditer(norm):
        h, mi = int(m.group(1)), int(m.group(2))
        if h > 12 or h == 0:
            add(m, h, mi, None)
        else:                                 # «7:00» — так и записано, без части суток
            key = f"{h}:{mi:02d}"
            if not any(a < m.end() and m.start() < b for a, b in taken):
                taken.append((m.start(), m.end()))
                out.append((m.start(), m.end(), key, set()))
    for m in _TIME_NOON_RX.finditer(norm):
        add(m, 12 if m.group(1).lower().startswith("полд") else 0, 0, "дня" if m.group(1).lower().startswith("полд")
            else "утра")
    return out


# --- числа словами внутри слова: «десятилетняя» = 10, «трёхкомнатная» = 3, «полчаса» = 0,5
_COMPOUND_PREFIX = [
    (1, "одно"), (2, "двух"), (3, "трех"), (4, "четырех"), (5, "пяти"), (6, "шести"), (7, "семи"), (8, "восьми"),
    (9, "девяти"), (10, "десяти"), (11, "одиннадцати"), (12, "двенадцати"), (13, "тринадцати"), (14, "четырнадцати"),
    (15, "пятнадцати"), (16, "шестнадцати"), (17, "семнадцати"), (18, "восемнадцати"), (19, "девятнадцати"),
    (20, "двадцати"), (30, "тридцати"), (40, "сорока"), (50, "пятидесяти"), (60, "шестидесяти"), (70, "семидесяти"),
    (80, "восьмидесяти"), (90, "девяноста"), (100, "сто"), (200, "двухсот"), (300, "трехсот"), (400, "четырехсот"),
    (500, "пятисот"), (1000, "тысяче"), (1.5, "полутора")]
_COMPOUND_RX = re.compile(
    r"^(" + "|".join(sorted((p for _, p in _COMPOUND_PREFIX), key=len, reverse=True)) + r")-?"
    r"(?:летн|летк|месячн|недельн|дневн|суточн|часов|минутн|секундн|комнатн|этажн|кратн|разов|процентн|местн|"
    r"тонн|метров|литров|граммов|килограммов|рублев|долларов|томн|серийн|звездочн|ядерн|колесн|дверн|значн|"
    r"миллионн|тысячн|ступенчат|уровнев|голов|сторонн|канальн|ядерн)\w*$")
_COMPOUND_VAL = {p: v for v, p in _COMPOUND_PREFIX}
# «пол-»: половина единицы; рядом — та же величина в меньшей единице («полчаса» = «30 минут»)
_HALF_RX = re.compile(r"^пол-?(часа|минуты|года|дня|суток|месяца|недели|века|литра|килограмма|кило|метра|"
                      r"тысячи|миллиона|миллиарда|сотни|дюжины)$")
_HALF_VAL = {"часа": (0.5, {"30"}), "минуты": (0.5, {"30"}), "года": (0.5, {"6"}), "дня": (0.5, {"12"}),
             "суток": (0.5, {"12"}), "месяца": (0.5, {"2", "15"}), "недели": (0.5, set()), "века": (0.5, {"50"}),
             "литра": (0.5, {"500"}), "килограмма": (0.5, {"500"}), "кило": (0.5, {"500"}), "метра": (0.5, {"50"}),
             "тысячи": (500, set()), "миллиона": (500000, set()), "миллиарда": (500000000, set()),
             "сотни": (50, set()), "дюжины": (6, set())}


def _valid_next(last, vk) -> bool:
    """Можно ли слово-число vk приписать к составному числу, последнее слово которого last:
    «сто двадцать пять» — да, «десять одиннадцать» («без десяти одиннадцать») — нет."""
    if last is None:
        return True
    if isinstance(last, int) and 100 <= last < 1000 and last % 100 == 0:
        return vk < 100
    if isinstance(last, int) and 20 <= last <= 90 and last % 10 == 0:
        return isinstance(vk, int) and 1 <= vk <= 9
    return False


# нумерация пунктов — не число факта (DEV-замер v2, P8): «1. Основатели…», «2) …», эмодзи-цифры «1️⃣»
_LINE_NUM_RX = re.compile(r"^\s*\d{1,2}[.)](?=\s|$)")
_KEYCAP_RX = re.compile("\\d\ufe0f?\u20e3")
_GLUED_NUM_RX = re.compile(r"(?<=[^\W\d_])\d+(?=[^\W\d_])")     # цифры между буквами: «B2B», «P2P», «H2O»


def _blank(m: re.Match) -> str:
    return " " * len(m.group(0))


def numbers_in(doc: tk.Doc) -> dict[str, dict]:
    """Значение → {'report', 'sents', 'n', 'alts'}. Слово «один» сверяется, но о нём не сообщается.
    'alts' — равнозначные записи того же значения («~10:50» = «10:50» или «22:50», «полчаса» = «30»).
    Нумерация пунктов в начале строки («1.», «2)») и эмодзи-цифры («1️⃣») числами не считаются."""
    found: dict[str, dict] = {}

    def add(val: str, i: int, report: bool = True, alts=()):
        rec = found.setdefault(val, {"report": False, "sents": [], "n": 0, "alts": set()})
        rec["report"] = rec["report"] or report
        rec["n"] += 1
        rec["alts"] |= set(alts)
        if i not in rec["sents"]:
            rec["sents"].append(i)

    for i, s in enumerate(doc.sents):
        txt = _KEYCAP_RX.sub(_blank, s.soft)
        txt = _GLUED_NUM_RX.sub(_blank, txt)          # «B2B», «P2P», «H2O» — термин, а не число факта
        if s.line_start:
            txt = _LINE_NUM_RX.sub(_blank, txt)
        for m in _DATE_RX.finditer(txt):
            add(m.group(0), i)
        txt = _DATE_RX.sub(lambda m: " " * len(m.group(0)), txt)
        for a, b, key, alts in time_exprs(tk.fold_yo(txt)):
            add(key, i, alts=alts)
            txt = txt[:a] + " " * (b - a) + txt[b:]
        for m in _NUM_RX.finditer(txt):
            ip = m.group(1).replace(" ", "")
            dec = (m.group(2) or "").rstrip("0")
            add(str(int(ip)) + ("." + dec if dec else ""), i)
        # числа словами, соседние слова складываются: «двадцать пять», «две тысячи»
        words = [t for t in (tk.make_tok(x) for x in tk.tokenize(txt)) if t.is_word]
        j = 0
        while j < len(words):
            v = _word_value(words[j])
            if v is None or words[j].is_num:
                mc = _COMPOUND_RX.match(words[j].low) if not words[j].is_num else None
                mh = _HALF_RX.match(words[j].low) if not words[j].is_num else None
                if mc:
                    cv = _COMPOUND_VAL[mc.group(1)]
                    add(_fmt(cv), i, report=cv != 1)
                elif mh:
                    hv, alts = _HALF_VAL[mh.group(1)]
                    add(_fmt(hv), i, alts=alts)
                j += 1
                continue
            prev = words[j - 1] if j > 0 else None
            if v in MULTIPLIERS and prev is not None and (prev.is_num or prev.text[:1].isdigit()):
                j += 1
                continue
            total, cur, k, only_one, last = 0, 0, j, True, None
            while k < len(words):
                vk = _word_value(words[k])
                if vk is None or words[k].is_num:
                    break
                if vk in MULTIPLIERS:
                    if cur == 0 and k > j and last is None:
                        break                       # «тысяча тысяч»: второе — отдельное слово
                    total += max(cur, 1) * vk
                    cur, last = 0, None
                else:
                    if not _valid_next(last, vk):
                        break
                    cur += vk
                    last = vk
                if vk != 1:
                    only_one = False
                k += 1
            add(_fmt(total + cur), i, report=not only_one)
            j = k
    return found


def _num_vals(v: str, rec: dict) -> set:
    return {v} | rec.get("alts", set())


def _num_show(v: str) -> str:
    return f"{v[1:]} (утра или вечера)" if v.startswith("~") else v


def _num_count(v: str, rec: dict, other: dict) -> int:
    """Сколько раз значение v (с равнозначными записями) встречается в other."""
    vals = _num_vals(v, rec)
    return sum(r["n"] for k, r in other.items() if _num_vals(k, r) & vals)


_NUMWORD_ALT = "|".join(p for _, p in _NUM_FALLBACK) + (
    r"|половин\w*|трет[ьиюей]\w*|четверт\w*|вдвое|втрое|вчетверо|впятеро|вдесятеро|десят(?:ок|ка|ков|ки)|"
    r"дюжин\w*|сотн\w*|полтысячи")
_NUMBER_AHEAD = rf"(?:(?:на|в|до|за|через|по|с)\s+)?(?=\d|(?:{_NUMWORD_ALT})\b)"
# приблизительность и граница при числе: «почти 300» ≠ «300», «около 300» ≠ «почти 300»
APPROX_CLASSES = {
    "приблизительно («около», «примерно»)":
        rf"(?:\bоколо|\bпримерно|\bприблизительно|\bпорядка|\bгде-то|\bплюс-минус|~)\s*{_NUMBER_AHEAD}",
    "граница («почти», «более», «не меньше»)":
        rf"(?:(?:\bпочти|\bчуть\s+(?:больше|меньше|более|менее)|\b(?:не\s+)?(?:более|менее|больше|меньше)(?:\s+чем)?|"
        rf"\bсвыше|\b(?:как\s+)?минимум|\bмаксимум)\s+|[<>≤≥]\s*){_NUMBER_AHEAD}",
}

# единица при числе: «900 рублей» ≠ «900 долларов»
UNIT_CLASSES = [
    ("руб.", r"руб\w*|₽"), ("долл.", r"доллар\w*|долл|бакс\w*|\$|usd"), ("евро", r"евро|€|eur"),
    ("тенге", r"тенге|₸"), ("%", r"%|процент\w*"), ("сек.", r"секунд\w*|сек"), ("мин.", r"минут\w*|мин"),
    ("ч", r"час|часа|часов|часам|часами|часах|ч"), ("дн.", r"день|дня|дней|дням|днями|днях|сутки|суток|дн"),
    ("нед.", r"недел\w*|нед"), ("мес.", r"месяц\w*|мес"), ("г.", r"год|года|году|годом|годам|годами|годах|лет"),
    ("км", r"км|километр\w*"), ("м", r"метр\w*"), ("кг", r"кг|килограмм\w*"), ("гр.", r"грамм\w*|гр"),
    ("ГБ", r"гб|gb|гигабайт\w*"), ("МБ", r"мб|mb|мегабайт\w*"), ("ТБ", r"тб|tb|терабайт\w*"),
    ("чел.", r"человек\w*|чел|людей"), ("раз", r"раз|раза"),
]
_UNIT_RX = [(u, re.compile(rf"^(?:{p})$", re.I)) for u, p in UNIT_CLASSES]
_NUM_UNIT_RX = re.compile(
    rf"(?<![\w.,])(\d{{1,3}}(?: \d{{3}})+|\d+(?:[.,]\d+)?|(?:{_NUMWORD_ALT}))(?![\w])"
    rf"\s*(?:[–—-]\s*\d+(?:[.,]\d+)?\s*)?(?:(?:тыс|млн|млрд)\.?\s*|(?:тысяч\w*|миллион\w*|миллиард\w*)\s+)?"
    rf"(%|₽|\$|€|₸|[^\W\d_]+)", re.I)
_CUR_PREFIX_RX = re.compile(r"([$€₽₸])\s*(\d{1,3}(?: \d{3})+|\d+(?:[.,]\d+)?)")


def _num_norm(s: str) -> str | None:
    s = s.lower()
    if s[:1].isdigit():
        s = s.replace(" ", "").replace(",", ".")
        ip, _, dec = s.partition(".")
        dec = dec.rstrip("0")
        return str(int(ip)) + ("." + dec if dec else "")
    for v, r in _NUM_FALLBACK_RX:
        if r.match(s):
            return _fmt(v)
    return None


def _unit_class(w: str) -> str | None:
    for u, r in _UNIT_RX:
        if r.match(w):
            return u
    return None


def number_units(doc: tk.Doc) -> Counter:
    """(число, класс единицы) → сколько раз: «900 рублей» → ('900', 'руб.')."""
    c: Counter = Counter()
    for s in doc.sents:
        for m in _NUM_UNIT_RX.finditer(s.norm):
            v, u = _num_norm(m.group(1)), _unit_class(m.group(2))
            if v is not None and u is not None:
                c[(v, u)] += 1
        for m in _CUR_PREFIX_RX.finditer(s.norm):
            v, u = _num_norm(m.group(2)), _unit_class(m.group(1))
            if v is not None and u is not None:
                c[(v, u)] += 1
    return c


# «сегодня» не берём: скилл велит снимать «Сегодня хочу поделиться» (YA-01), и A2 мешал бы этой правке.
# «среду» — только как день: «в среду», «по средам», «эту среду» (не «в окружающую среду»)
MONTHS_RX = re.compile(r"\b(?:январ|феврал|март|апрел|ма[йяюе]\b|июн|июл|август|сентябр|октябр|ноябр|декабр|"
                       r"понедельник|вторник|четверг|пятниц|суббот|воскресень|вчера|завтра|позавчера|послезавтра)\w*",
                       re.I)
WEDNESDAY_RX = re.compile(r"\b(?:в|во|по|до|к|эту|ту|прошлую|следующую|ближайшую|каждую)\s+(сред(?:у|ам))\b"
                          r"(?!\s+(?:обитания|разработки|исполнения|выполнения|программирования|окружения))", re.I)


def _date_words(doc: tk.Doc) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for i, s in enumerate(doc.sents):
        for m in MONTHS_RX.finditer(s.norm):
            key = m.group(0).lower()[:4]
            out.setdefault(key, []).append(i)
        for m in WEDNESDAY_RX.finditer(s.norm):
            out.setdefault("сред", []).append(i)
    return out


_START_PUNCT = frozenset({":", "—", "–", "-", "(", "…", "...", ".", "!", "?", ";"})
_NEUTRAL_PUNCT = frozenset({"**", "*", "__", "_", '"', "«", "»", "•", "▪", "●", "◦"})


def name_candidates(doc: tk.Doc) -> list[tuple[set, str, int]]:
    """Имена и названия: заглавная не в начале фразы, латиница, аббревиатуры, словарные имена.
    Начало фразы — и после нумерации, разметки и эмодзи («3. **Приготовьте…**», «2️⃣ **Компетенции**»,
    «плечами 🙂 Суть простая»), и после точки внутри «**Аватар.** При…», которую razdel не режет."""
    out = []
    for i, s in enumerate(doc.sents):
        start = True                    # заглавная в начале фразы — не признак имени
        lead = True                     # пока идут только номер пункта и знаки
        for t in s.toks:
            if t.is_word:
                cand = False
                if t.is_num or t.text[:1].isdigit():
                    cand = False
                elif t.is_latin:
                    cand = len(t.text) >= 2
                elif (t.text[:1].isupper() and len(t.text) >= 2 and t.low not in ("вы", "вас", "вам", "вами")
                      and not t.low.startswith("ваш")):
                    caps = t.text.isupper()
                    proper = tk.is_proper(t.w) or (t.w is not None and not t.w.known and len(t.text) > 3)
                    cand = caps or proper or (not start and not (t.w is not None and t.w.pos in ("NPRO", "CONJ", "PRCL")))
                if cand:
                    out.append((tk.tok_variants(t), t.text, i))
                lead = lead and t.is_num and len(t.text) <= 2
                start = lead
            elif t.text in _START_PUNCT or tk.EMOJI_RX.search(t.text) or "⃣" in t.text:
                start = True
            elif t.text not in _NEUTRAL_PUNCT:
                start = False
    return out


NEG_WORDS = frozenset("не ни нет нельзя никогда ничего ничто никто никак нигде никуда ниоткуда никакой никакая "
                      "никакое никакие никакого никаких никому никого ничем ничему никем".split())
_FUNC_FALLBACK = frozenset("в во на с со к ко у из за от до для при через про под над без о об по и а но же ли бы "
                           "то так даже очень только уже еще ещё совсем вовсе всегда".split())


def _next_content(ws: list, j: int):
    """Первое знаменательное слово после позиции j (предлоги, союзы, частицы пропускаются)."""
    for t in ws[j + 1:j + 4]:
        if t.low in NEG_WORDS:
            continue
        if t.w is not None:
            if t.w.pos in ("PREP", "CONJ", "PRCL"):
                continue
        elif t.low in _FUNC_FALLBACK:
            continue
        return t
    return None


_CLAUSE_PUNCT = frozenset({",", ";", ":", "—", "–", "-", ".", "!", "?", "(", ")", "...", "…", '"', "«", "»"})


def _clause_words_after(s: tk.Sent, t: tk.Tok) -> list[tk.Tok]:
    """Слова после токена t до ближайшего знака препинания: отрицание не переходит через запятую
    («порога нет, и единственное…» — «единственное» не под отрицанием)."""
    toks = s.toks
    k = next(n for n, x in enumerate(toks) if x is t)
    out = [t]
    for x in toks[k + 1:]:
        if not x.is_word:
            if x.text in _CLAUSE_PUNCT:
                break
            continue
        out.append(x)
    return out


_BOUND_COMP = frozenset("ниже выше меньше больше более менее раньше ранее позже позднее дольше старше моложе младше "
                        "реже чаще дороже дешевле длиннее короче хуже лучше".split())


def _numberish(t: tk.Tok) -> bool:
    return bool(re.search(r"\d", t.text)) or _word_value(t) is not None


def _bound_after(ws: list, j: int) -> bool:
    """«не ниже F50», «не позже 10-го», «не больше трёх»: граница при числе, а не отрицание факта."""
    if j + 1 >= len(ws) or ws[j + 1].low not in _BOUND_COMP:
        return False
    rest = [t for t in ws[j + 2:j + 5] if t.low not in ("чем", "в", "на", "за", "через", "до", "с")]
    if not rest:
        return False
    # «F50» razdel режет на «F» и «50»: число может стоять вторым токеном после буквы-марки
    return _numberish(rest[0]) or (len(rest) > 1 and rest[0].is_latin and len(rest[0].text) <= 3
                                   and _numberish(rest[1]))


def neg_pairs(doc: tk.Doc) -> list[tuple[str, int, str]]:
    """(ключ слова после отрицания, фраза, текст пары). «не просто X, а Y» пропускается (YA-07),
    «не ниже F50» и другие границы при числе — тоже (их сверяет A1).
    Слово ищется в той же части фразы, до запятой или тире."""
    out = []
    for i, s in enumerate(doc.sents):
        ws = s.words
        for j, t in enumerate(ws):
            if t.low not in NEG_WORDS:
                continue
            nxt = ws[j + 1] if j + 1 < len(ws) else None
            if (t.low == "не" and nxt is not None and nxt.low in ("просто", "только", "столько", "лишь")
                    and re.search(rf"не {nxt.low}\b[^.!?]{{1,120}}?(?:,\s*(?:а|но)\b|\s+но\s+и\b)", s.norm, re.I)):
                continue                      # «не просто / не только X, а / но и Y» — не отрицание факта
            if t.low == "не" and _bound_after(ws, j):
                continue
            cw = _clause_words_after(s, t)
            c = _next_content(cw, 0)
            key = tk.word_key(c) if c is not None else ""
            out.append((key, i, " ".join(x.text for x in cw[:cw.index(c) + 1]) if c is not None else t.text))
    return out


NEG_LIKE = NEG_WORDS | {"без"}


def _plain_count(sents: list, variants: set) -> tuple[int, bool]:
    """(сколько раз слово стоит без отрицания в пределах 3 слов перед ним, есть ли во фразах отрицание вообще).
    «без» здесь считается отрицанием: «нет проблем» → «без проблем» — не переворот."""
    n, any_neg = 0, False
    for s in sents:
        ws = s.words
        any_neg = any_neg or any(x.low in NEG_LIKE for x in ws)
        for j, t in enumerate(ws):
            if tk.tok_variants(t) & variants and not any(x.low in NEG_LIKE for x in ws[max(0, j - 3):j]):
                n += 1
    return n, any_neg


def _bez_pairs(doc: tk.Doc) -> Counter:
    """Ключи слов после «без»: компенсируют пропавшее «не / нет / никаких» при том же слове."""
    c = Counter()
    for s in doc.sents:
        ws = s.words
        for j, t in enumerate(ws):
            if t.low == "без":
                x = _next_content(_clause_words_after(s, t), 0)
                if x is not None:
                    c[tk.word_key(x)] += 1
    return c


def _neg_lost(a: tk.Doc, b: tk.Doc, ap: list, bp: list, al: list, al_best: list):
    """Отрицания текста a, которых нет в b: (пропавшие пары, перевороты (фраза a, фраза b, пара), компенсировано «без»).
    Переворот: слово осталось в b без отрицания чаще, чем было, и в лучшей фразе b отрицаний нет вовсе."""
    bc = Counter(k for k, _, _ in bp)
    used = Counter()
    bez = _bez_pairs(b) - _bez_pairs(a)
    lost, flips, compensated = [], [], 0
    for key, i, text in ap:
        used[key] += 1
        if used[key] <= bc.get(key, 0):
            continue
        if key and bez[key] > 0:              # «никаких претензий» → «без претензий»
            bez[key] -= 1
            compensated += 1
            continue
        win = [b.sents[j] for j in sorted(al[i])]
        if _prefix_absorbed(a.sents[i], win):  # «не считался модным» → «считался немодным»
            compensated += 1
            continue
        lost.append((text, i))
        if not key or al_best[i] is None:
            continue
        variants = {key}
        a_plain, _ = _plain_count([a.sents[i]], variants)
        b_plain, _ = _plain_count(win, variants)
        best_plain, best_neg = _plain_count([b.sents[al_best[i]]], variants)
        if (best_plain > 0 and not best_neg and b_plain > a_plain
                and not any(_neg_prefixed(x) for x in b.sents[al_best[i]].words)):
            flips.append((i, al_best[i], text))
    return lost, flips, compensated


_NEG_PREFIX_POS = frozenset({"ADJF", "ADJS", "ADVB", "PRTF", "PRTS", "PRED", "COMP"})
# слова с «не-», которые давно не значат «не X»
_NEG_PREFIX_LEXICAL = frozenset("несколько недавно немного немножко небольшой недалеко нередко невероятный невероятно "
                                "незадолго некоторый некий неважно".split())


def _neg_rest(t: tk.Tok) -> str | None:
    """Лемма слова без приставки «не-», если слово — отрицание через приставку («немодный» → «модный»)."""
    if t.w is None or t.w.pos not in _NEG_PREFIX_POS or "Apro" in t.w.tags:
        return None
    if not t.low.startswith("не") or len(t.low) < 5 or t.w.lemma in _NEG_PREFIX_LEXICAL or t.low in _NEG_PREFIX_LEXICAL:
        return None
    rest = tk.parse(t.low[2:])
    return rest.lemma if (rest and rest.known and rest.pos == t.w.pos) else None


def _neg_prefixed(t: tk.Tok) -> bool:
    """«немодный», «несложно», «неудачный»: отрицание в приставке."""
    return _neg_rest(t) is not None


def _prefix_absorbed(a_sent: tk.Sent, b_sents: list) -> bool:
    """Отрицание ушло в приставку: в b есть «немодным», а в a — «модным» при «не»."""
    a_keys = {tk.word_key(t) for t in a_sent.words}
    return any(_neg_rest(t) in a_keys for s in b_sents for t in s.words if _neg_rest(t))


_INF = r"\w+(?:ть|ти|чь)(?:ся|сь)?"
MODAL_CLASSES = {
    "долженствование («надо», «нужно», «должен»)":
        r"\b(?:надо|нужно|необходимо|должен|должна|должно|должны|обязан|обязана|обязано|обязаны|обязательно|"
        r"следует|приходится|пришлось|придется|понадобится)\b",
    # возможность и разрешение — один класс: «позволяет достичь» → «с ней можно добиться» — та же модальность,
    # а «позволит сократить» → «сократит» и «может помочь» → «помогает» — возможность стала фактом
    "возможность («можно», «может», «позволяет»)":
        r"\b(?:можно|разрешено|разрешается|вправе|допускается|допустимо|возможно|"
        r"мож(?:ет|ешь|ем|ете)|могу|могут|мог|могла|могло|могли|мочь|смож\w+|смог|смогла|смогло|смогли|"
        r"позвол(?:я\w*|ит|ят|ил|ила|ило|или|ить)|способ(?:ен|на|но|ны)|в состоянии|"
        rf"получ(?:ится|ается|илось|алось|аться)\s+(?:\w+\s+)?{_INF}|"
        rf"(?:помога(?:ет|ют|л|ла|ло|ли|ть)|помо(?:жет|гут|г|гла|гло|гли|чь))\s+(?:\w+\s+){{0,2}}?{_INF}|"
        r"(?:да[её]т|дают|даст|дадут|дало|дала|дал|дали|давать|дать|есть|будет|была|было|появится|появилась)\s+"
        rf"(?:\w+\s+)?возможност\w+|возможност[ьи]\s+{_INF})\b",
    "запрет («нельзя»)": r"\b(?:нельзя|запрещено|запрещается|запрещен\w*)\b",
    "совет («стоит», «рекомендуется»)":
        rf"\b(?:стоит|стоило)\s+(?:\w+\s+)?{_INF}\b|\bрекомендуе?тся\b|\bсоветую\b|\bсоветуем\b",
}


def modal_hits(doc: tk.Doc, pattern: str) -> list[tuple[int, str]]:
    r = rx(pattern)
    return [(i, m.group(0)) for i, s in enumerate(doc.sents) for m in r.finditer(s.norm)]


# --------------------------------------------------------------- рамки мнения и источники (A11)
# «строгие» формы ищутся в исходнике, «мягкие» — в результате: «по их мнению» → «они считают, что» — источник на месте.
_ADV_FRAME = r"(?:(?:все|всё|же|лично|тоже|по-прежнему|искренне|твердо|абсолютно|совершенно|действительно|правда)\s+)?"
OPINION_STRICT = (
    rf"\bя\s+{_ADV_FRAME}(?:уверен|уверена|убежден|убеждена|считаю|думаю|полагаю)\b"
    rf"|\bмы\s+{_ADV_FRAME}(?:уверены|убеждены|считаем|думаем|полагаем)\b"
    r"|(?:^\W*|\b(?:и|а|но|да|не)\s+(?:—\s*)?)(?:уверен|уверена|уверены|убежден|убеждена|считаю|считаем|думаю|думаем|"
    r"полагаю)\b"
    r"|\b(?:мне|нам)\s+(?:\w+\s+)?(?:кажется|казалось|думается)\b"
    r"|\bпо-моему\b|\bпо-нашему\b|\bна (?:мой|наш) взгляд\b|\bпо (?:моему|нашему) (?:мнению|убеждению|ощущению)\b"
    r"|\bс (?:моей|нашей) точки зрения\b|\bкак по мне\b"
)
OPINION_LENIENT = OPINION_STRICT + (
    r"|\b(?:уверен|уверена|уверены|убежден\w*|считаю|считаем|думаю|думаем|полагаю|полагаем|кажется|казалось)\b"
    r"|\b(?:наверное|вероятно|видимо|похоже|по-видимому|скорее всего|пожалуй|вроде бы)\b"
)
_SRC_NOUN = (r"(?:опыту|данным|словам|мнению|оценкам?|подсчетам|сведениям|наблюдениям|расчетам|прогнозам?|версии|"
             r"ощущениям|информации|заявлению|утверждению|сообщению)")
_SAY_VERBS = (r"(?:пишет|пишут|писал[аи]?|считает|считают|считал[аи]?|говорит|говорят|говорил[аи]?|сообщает|сообщают|"
              r"сообщил[аи]?|утверждает|утверждают|утверждал[аи]?|отмечает|отмечают|отметил[аи]?|заявляет|заявляют|"
              r"заявил[аи]?|рассказывает|рассказывают|рассказал[аи]?|полагает|полагают|уверяет|уверяют|признает|"
              r"признают|признал[аи]?|подсчитал[аи]?|выяснил[аи]?|объясняет|объясняют|объяснил[аи]?|поясняет|"
              r"пояснил[аи]?|указывает|указывают|указал[аи]?|предупреждает|предупреждают|предупредил[аи]?)")
SOURCE_STRICT = (
    r"\bпо (?:моему|нашему) (?:опыту|данным|подсчетам|наблюдениям|расчетам|ощущениям|сведениям)\b"
    rf"|\bпо (?:их|его|ее|вашему|твоему) {_SRC_NOUN}\b"
    rf"|\bпо {_SRC_NOUN}\s+(?!(?:моему|нашему|их|его|ее|вашему|твоему)\b)[^\W\d_]"
    r"|\bсогласно\s+(?:данным|исследованию|исследованиям|опросу|опросам|отчету|оценкам?|прогнозу|информации|"
    r"словам|мнению|подсчетам|статистике)\b"
    rf"|\bкак {_SAY_VERBS}\b"
    r"|\b(?:считает|считают|считал|считала|считали|полагает|полагают|уверен|уверена|уверены|убежден|убеждена|"
    r"убеждены|уверяет|уверяют|утверждает|утверждают|думает|думают)\s*(?:,\s*что\b|:)"
)
SOURCE_LENIENT = SOURCE_STRICT + (
    rf"|\b{_SAY_VERBS}\b|\b(?:сказал|сказала|сказали|уточнил[аи]?|ссылаясь|цитирует|цитата)\b"
    r"|\bподчерк(?:нул[аи]?|ивает|ивают)\b|\bдобавил[аи]?\b|\bпризнал(?:ся|ась|ись)\b|\bназвал[аи]?\b"
    r"|\bпо (?:словам|мнению|данным|оценкам?|подсчетам|прогнозам?|информации|сведениям)\b|\bсогласно\s+[^\W\d_]"
    r"|\b(?:на|с) (?:их|его|ее) (?:взгляд|точки зрения)\b"
    r"|\bопыт\w*|\bпо моим наблюдениям\b|\bя (?:заметил|заметила|замечал|замечала|видел|видела|наблюдал|наблюдала)\b"
    r"|\bсчита(?:ет|ют|л|ла|ли)\b|\bуверен[аы]?\b|\bубежден[аы]?\b"
)
FRAME_CLASSES = (("мнение", "Рамка мнения пропала", OPINION_STRICT, OPINION_LENIENT),
                 ("источник", "Источник или опыт пропал", SOURCE_STRICT, SOURCE_LENIENT))


def _mask(s: str, r: re.Pattern) -> str:
    return r.sub(lambda m: " " * len(m.group(0)), s)


def frame_hits(doc: tk.Doc, strict: bool = True) -> dict[str, list[tuple[int, str]]]:
    """Класс → [(фраза, совпадение)]. Рамка мнения ищется первой и маскируется: «я уверен, что» — мнение,
    «эксперты уверены, что» — источник."""
    out: dict[str, list[tuple[int, str]]] = {}
    for i, s in enumerate(doc.sents):
        txt = s.norm.strip()
        for name, _, sp, lp in FRAME_CLASSES:
            r = rx(sp if strict else lp)
            ms = list(r.finditer(txt))
            out.setdefault(name, []).extend((i, m.group(0).strip()) for m in ms)
            if name == "мнение":
                txt = _mask(txt, rx(OPINION_STRICT))
    return out


def _frames_lost(src: tk.Doc, res: tk.Doc, al: list[set[int]]) -> list[Finding]:
    """A11: рамка мнения или источник стояли во фразе исходника, а в выровненных фразах результата
    (лучшая ± 1) нет никакой рамки того же класса. Вторую рамку у той же мысли снимать можно."""
    out = []
    sh, rh = frame_hits(src, strict=True), frame_hits(res, strict=False)
    rs = frame_hits(res, strict=True)
    for name, title, _, _ in FRAME_CLASSES:
        a, b = sh.get(name, []), rh.get(name, [])
        if not a or len(rs.get(name, [])) >= len(a):
            continue                       # все строгие рамки на месте: окно просто не выровнялось
        b_sents = {j for j, _ in b}
        lost = []
        for i in dict.fromkeys(i for i, _ in a):
            if al[i]:
                if not (al[i] & b_sents):
                    lost.append(i)
            elif len(b) < len(a):          # фраза не выровнялась: сверяем только общее число
                lost.append(i)
        if not lost:
            continue
        what = ", ".join(dict.fromkeys(f"«{m}»" for i, m in a if i in lost))
        frs = []
        for i in lost[:2]:
            frs.append(_fr("исходник", src.sents[i].raw, ", ".join(m for k, m in a if k == i)))
            if al[i]:
                ki = tk.content_keys(src.sents[i].words)
                best = max(sorted(al[i]), key=lambda x: len(ki & tk.content_keys(res.sents[x].words)))
                frs.append(_fr("результат", res.sents[best].raw, "без рамки"))
        hint = ("Рамку перестроить, но не удалять: «Я уверен: X» → «Я уверен, что X». Без рамки мнение становится "
                "фактом. Снять можно только вторую рамку у той же мысли." if name == "мнение" else
                "Источник вернуть: «по моему опыту», «по их данным», «как пишет X» — часть факта. "
                "Без него опыт или чужое мнение становится общим утверждением.")
        out.append(Finding("A", "A11", title, "hard", f"нет в результате: {what}", frs[:MAX_FRAGS], hint))
    return out


_SUBJ_WORDS = frozenset({"бы", "б", "чтобы", "чтоб"})


def _subjunctive(s: tk.Sent, t: tk.Tok) -> bool:
    """Форма на -л в сослагательном наклонении: «чтобы всё настроил», «занимался бы» — это не прошедшее время.
    Назад — до 6 слов в той же части фразы, вперёд — до 2 слов («бы»)."""
    toks = s.toks
    k = next(n for n, x in enumerate(toks) if x is t)
    seen = 0
    for x in reversed(toks[:k]):
        if not x.is_word:
            if x.text in _CLAUSE_PUNCT:
                break
            continue
        if x.low in _SUBJ_WORDS:
            return True
        seen += 1
        if seen >= 6:
            break
    after = [x for x in toks[k + 1:k + 4] if x.is_word][:2]
    return any(x.low in ("бы", "б") for x in after)


def finite_verbs(doc: tk.Doc) -> list[dict]:
    out = []
    for i, s in enumerate(doc.sents):
        for t in s.words:
            if t.w is None or t.w.pos not in ("VERB", "INFN") or t.w.lemma == "быть":
                continue
            tags = t.w.tags
            tense = ("past" if "past" in tags else "pres" if "pres" in tags else "futr" if "futr" in tags
                     else "impr" if "impr" in tags else None)
            if tense == "past" and _subjunctive(s, t):
                tense = "subj"
            aspect = "perf" if "perf" in tags else "impf" if "impf" in tags else None
            out.append(dict(lemma=t.w.lemma, tense=tense, aspect=aspect, word=t.text, sent=i))
    return out


TENSE_RU = {"past": "прошедшее", "pres": "настоящее", "futr": "будущее", "impr": "повелительное",
            "subj": "сослагательное", None: "инфинитив"}


def _aspect_partners(a: str, b: str) -> bool:
    if a == b or a.endswith(("ся", "сь")) != b.endswith(("ся", "сь")):
        return False                      # «масштабировать» / «масштабироваться» — не видовая пара
    for x, y in ((a, b), (b, a)):
        if x.endswith(y) and 1 <= len(x) - len(y) <= 4:
            return True
    cp = 0
    for ch1, ch2 in zip(a, b):
        if ch1 != ch2:
            break
        cp += 1
    return cp >= 3 and cp >= min(len(a), len(b)) - 3


def alignment(src: tk.Doc, res: tk.Doc) -> tuple[list[set[int]], list[int | None]]:
    """Для каждой фразы исходника — окно похожих фраз результата (лучшая ± 1) и сама лучшая."""
    rk = [tk.content_keys(s.words) for s in res.sents]
    win, best_j = [], []
    scale = (len(res.sents) - 1) / max(1, len(src.sents) - 1)
    for i, s in enumerate(src.sents):
        k = tk.content_keys(s.words)
        best, bj = 0.0, None
        for j, r in enumerate(rk):
            if not k:
                break
            sc = len(k & r) / len(k)
            # при равном счёте — фраза ближе к ожидаемому месту («Что я считаю успехом?» и
            # «Что ты считаешь успехом?» в одном тексте)
            if sc > best or (sc == best and bj is not None and sc > 0
                             and abs(j - i * scale) < abs(bj - i * scale)):
                best, bj = sc, j
        best_j.append(bj)
        win.append(set() if bj is None else {x for x in (bj - 1, bj, bj + 1) if 0 <= x < len(res.sents)})
    return win, best_j


LIST_LINE_RX = re.compile(r"^\s*(?:[-*•–—▪●◦]|\d{1,2}[.)]|[a-zа-я]\))\s+(\S.*)$")


def block_lists(doc: tk.Doc) -> list[list[str]]:
    lists, cur = [], []
    for raw in doc.mlines:
        m = LIST_LINE_RX.match(raw)
        if not m and tk.EMOJI_RX.match(raw.strip()[:1] or " "):
            m = re.match(r"^\s*\S+\s+(\S.*)$", raw)
        if m:
            cur.append(m.group(1))
        else:
            if len(cur) >= 2:
                lists.append(cur)
            cur = []
    if len(cur) >= 2:
        lists.append(cur)
    return lists


def inline_lists(doc: tk.Doc) -> list[tuple[int, list[str]]]:
    out = []
    for i, s in enumerate(doc.sents):
        if s.norm.count(",") < 1:
            continue
        for clause in re.split(r"[:;—()]", s.soft):
            items = _enum_items(clause)
            if len(items) >= 3:
                out.append((i, items))
    return out


def _item_toks(item: str) -> list[tk.Tok]:
    return [tk.make_tok(t) for t in tk.tokenize(tk.canon_keep_yo(item)) if any(ch.isalnum() for ch in t)]


def _evaluative(items: list[str]) -> bool:
    if not tk.has_morph():
        return False
    for it in items:
        toks = _item_toks(it)
        ws = [t for t in toks if t.w is not None and t.w.pos not in ("CONJ", "PRCL", "PREP")]
        if len(ws) != 1 or ws[0].w.pos not in ("ADJF", "ADJS", "ADVB", "COMP", "PRTF", "PRTS"):
            return False
    return True


def _item_present(item: str, res_keys: set) -> bool:
    toks = _item_toks(item)
    keys = [tk.tok_variants(t) for t in toks if tk.is_content(t)]
    if not keys:
        keys = [tk.tok_variants(t) for t in toks if len(t.low) >= 3 and not t.is_num]
    if not keys:
        return True
    hit = sum(1 for v in keys if v & res_keys)
    return hit >= math.ceil(len(keys) / 2)


# --------------------------------------------------------------- замок цитат (A12, DEV-замер v2, P9)
QUOTE_RX = re.compile(r"«([^«»\n]{1,600})»|„([^„“”\n]{1,600})[“”]|“([^“”\n]{1,600})”|\"([^\"\n]{1,600})\"")
_NAME_LIKE_POS = frozenset({"VERB", "INFN", "GRND", "PRTS", "PRED"})


def quotes_in(text: str) -> list[str]:
    """Тексты в кавычках: «ёлочки», „лапки“, “английские”, прямые (по парам в строке)."""
    return [next(g for g in m.groups() if g is not None) for m in QUOTE_RX.finditer(text)]


def _quote_words(q: str) -> list[tk.Tok]:
    return [t for t in (tk.make_tok(x) for x in tk.tokenize(tk.canon_keep_yo(q))) if t.is_word]


def _name_like(ws: list[tk.Tok]) -> bool:
    """Короткое название в кавычках («Истребитель проблем», «Боржоми»): его можно склонять."""
    return len(ws) <= 3 and not any(t.w is not None and t.w.pos in _NAME_LIKE_POS for t in ws)


def _quote_kept(ws: list[tk.Tok], res_lows: str, res_keys: str) -> bool:
    if " " + " ".join(t.low for t in ws) + " " in res_lows:
        return True
    return _name_like(ws) and "|" + "|".join(tk.word_key(t) for t in ws) + "|" in res_keys


def quotes_changed(src: tk.Doc, res: tk.Doc) -> list[tuple[str, int | None]]:
    """Цитаты исходника, которых нет в результате дословно (с точностью до «ё», регистра, вида кавычек
    и знаков препинания). Короткое название без глагола можно склонять. Цитата на полтекста — это обёртка
    ответа («Вот пост: «…»»), а не цитата: не сверяется. Ссылки, почта и @-упоминания внутри цитаты не
    сверяются (в разборе текста они замаскированы). Номер фразы — первая фраза цитаты, которой в результате нет."""
    rw = res.words
    res_lows = " " + " ".join(t.low for t in rw) + " "
    res_keys = "|" + "|".join(tk.word_key(t) for t in rw) + "|"
    out, seen = [], set()
    for m in QUOTE_RX.finditer(src.masked):
        g = next(k for k in range(1, 5) if m.group(k) is not None)
        q = m.group(g)
        ws = _quote_words(q)
        key = " ".join(t.low for t in ws)
        if not ws or key in seen or len(ws) * 2 > max(src.n_words, 1):
            continue
        seen.add(key)
        if _quote_kept(ws, res_lows, res_keys):
            continue
        a, b = m.start(g), m.end(g)
        inside = [i for i, s in enumerate(src.sents) if s.start < b and s.end > a]
        where = inside[0] if inside else None
        for i in inside:                 # первая фраза, на которой начало цитаты перестаёт совпадать
            head = _quote_words(src.masked[a:min(b, src.sents[i].end)])
            if " " + " ".join(t.low for t in head) + " " not in res_lows:
                where = i
                break
        out.append((src.text[a:b], where))
    return out


def block_a(src: tk.Doc, res: tk.Doc, mode: str, prov: "Prov | None" = None) -> list[Finding]:
    """Факт-замок. С prov.distinct (v4: --draft и источник) src — черновик: пропажа считается потерей, только если
    это есть в источнике или материале; снятое М черновика уходит в prov.cleaned (E7, чистка), а то, что
    вернули из источника, не считается новым."""
    out: list[Finding] = []
    write = mode == "write"
    pv = prov if (prov is not None and prov.distinct and prov.ref is not None and not write) else None
    al, al_best = alignment(src, res)
    pairs = tk.strong_pairs(src, res)           # выровненные пары фраз по леммам (A3, A6)

    def src_sents(ids, limit=MAX_FRAGS):
        return [_fr("исходник", src.sents[i].raw) for i in list(dict.fromkeys(ids))[:limit]]

    def res_sents(ids, limit=MAX_FRAGS):
        return [_fr("результат", res.sents[i].raw) for i in list(dict.fromkeys(ids))[:limit]]

    def m_sent(i) -> bool:
        """Фраза черновика без опоры в источнике и материале (её снятие — чистка)."""
        return pv is not None and i is not None and not pv.sent_backed(src.sents[i])

    def clean(what: str, i=None):
        if pv is not None:
            pv.cleaned.append((what, src.sents[i].raw.strip() if i is not None else ""))

    # --- числа (цифрой, словом, временем суток: «22:00» = «десять вечера», «полчаса» = «30 минут»)
    sn, rn = numbers_in(src), numbers_in(res)
    lost = [v for v, r in sn.items() if r["report"] and _num_count(v, r, rn) == 0]
    new = [v for v, r in rn.items() if r["report"] and _num_count(v, r, sn) == 0]
    if pv is not None:
        for v in [v for v in lost if not pv.num_backed(v, sn[v])]:
            clean(f"число «{_num_show(v)}»", sn[v]["sents"][0])
        lost = [v for v in lost if pv.num_backed(v, sn[v])]
        new = [v for v in new if not pv.num_backed(v, rn[v])]     # вернули из источника — не выдумка
    if lost and not write:
        out.append(Finding("A", "A1", "Числа: потеряны", "hard",
                           "нет в результате: " + ", ".join(f"«{_num_show(v)}»" for v in lost),
                           [f for v in lost for f in src_sents(sn[v]["sents"], 1)][:MAX_FRAGS],
                           "Вернуть каждое число на место (цифрой или словом, как было)."))
    if new:
        out.append(Finding("A", "A1", "Числа: новые", "hard",
                           "нет в исходнике: " + ", ".join(f"«{_num_show(v)}»" for v in new),
                           [f for v in new for f in res_sents(rn[v]["sents"], 1)][:MAX_FRAGS],
                           "Убрать выдуманные числа; приблизительное не делать точным."))
    if not write:
        # число осталось, но встречается реже: «2 лицензии для продаж и 2 для поддержки» → «2 … и для поддержки»
        fewer = [(v, r["n"], c) for v, r in sn.items() if r["report"]
                 for c in [_num_count(v, r, rn)] if 0 < c < r["n"]]
        if pv is not None:
            for v, _, _ in fewer:
                if not pv.num_backed(v, sn[v]):
                    clean(f"повтор числа «{_num_show(v)}»", sn[v]["sents"][-1])
            fewer = [(v, a, b) for v, a, b in fewer if pv.num_backed(v, sn[v])]
        if fewer:
            out.append(Finding("A", "A1", "Числа: встречаются реже", "hard",
                               "; ".join(f"«{_num_show(v)}»: было {a}, стало {b}" for v, a, b in fewer),
                               [f for v, _, _ in fewer for f in src_sents(sn[v]["sents"], 2)][:MAX_FRAGS],
                               "Каждое упоминание числа исходника — на месте: повтор числа несёт отдельный факт."))
        # единица при том же числе: «900 рублей» → «900 долларов»
        su, ru = number_units(src), number_units(res)
        swaps, swap_frs = [], []
        for (v, u), n in su.items():
            if ru.get((v, u), 0) >= n:
                continue
            other = [u2 for (v2, u2), n2 in ru.items() if v2 == v and u2 != u and n2 > su.get((v2, u2), 0)]
            if other:
                swaps.append(f"«{v} {u}» → «{v} {other[0]}»")
                swap_frs += src_sents(sn.get(v, {}).get("sents", []), 1) + res_sents(rn.get(v, {}).get("sents", []), 1)
        if swaps:
            out.append(Finding("A", "A1", "Числа: другая единица", "hard", "; ".join(swaps[:6]), swap_frs[:MAX_FRAGS],
                               hint="Единицы и валюты при числах — как в исходнике."))
        # «почти / около / более N» — приблизительное не делать точным и наоборот
        for name, pat in APPROX_CLASSES.items():
            a, b = modal_hits(src, pat), modal_hits(res, pat)
            if len(a) == len(b):
                continue
            what = "пропала" if len(b) < len(a) else "появилась"
            frs = src_sents([i for i, _ in a]) if len(b) < len(a) else res_sents([j for j, _ in b])
            out.append(Finding("A", "A1", f"Числа: {what} оговорка — {name}", "hard",
                               f"в исходнике {len(a)} ({', '.join(sorted({m.strip() for _, m in a})) or '—'}), "
                               f"в результате {len(b)} ({', '.join(sorted({m.strip() for _, m in b})) or '—'})",
                               frs[:MAX_FRAGS],
                               "«почти 300» ≠ «300» ≠ «около 300»: оговорку при числе брать из исходника."))
    # --- даты словами
    sd, rd = _date_words(src), _date_words(res)
    dl = [k for k in sd if k not in rd]
    dn = [k for k in rd if k not in sd]
    if pv is not None:
        pd_ = _date_words(pv.ref)
        for k in [k for k in dl if k not in pd_]:
            clean(f"дата «{k}…»", sd[k][0])
        dl = [k for k in dl if k in pd_]
        dn = [k for k in dn if k not in pd_]
    if (dl and not write) or dn:
        frs = [f for k in dl for f in src_sents(sd[k], 1)] + [f for k in dn for f in res_sents(rd[k], 1)]
        out.append(Finding("A", "A2", "Даты и дни словами", "hard",
                           ("потеряно: " + ", ".join(dl) + "; " if dl and not write else "")
                           + ("новое: " + ", ".join(dn) if dn else ""),
                           frs[:MAX_FRAGS], "Месяцы, дни недели, «вчера/завтра» — как в исходнике."))
    # --- имена и названия. Жёстко — только если фраза уцелела (есть выровненная пара по леммам), а имя в ней
    #     пропало или появилось; на пересказе, где фраза переписана целиком, — подсказка (DEV-замер v2, P9:
    #     на контроле A3 давало 10 находок, большинство — однокоренные замены и синонимы)
    s_all, r_all = tk.all_keys(src), tk.all_keys(res)
    src_paired = {i for i, _ in pairs}
    res_paired = {j for _, j in pairs}
    lost_n, seen = [], set()
    if not write:
        for var, text, i in name_candidates(src):
            if not (var & r_all) and text.lower() not in seen:
                seen.add(text.lower())
                lost_n.append((text, i))
    if pv is not None:
        src_names = {t.lower(): v for v, t, _ in name_candidates(src)}
        for t, i in [(t, i) for t, i in lost_n if not pv.name_backed(src_names.get(t.lower(), set()))]:
            clean(f"имя «{t}»", i)
        lost_n = [(t, i) for t, i in lost_n if pv.name_backed(src_names.get(t.lower(), set()))]
    new_n, seen = [], set()
    for var, text, i in name_candidates(res):
        if not (var & s_all) and text.lower() not in seen and not (pv is not None and pv.name_backed(var)):
            seen.add(text.lower())
            new_n.append((text, i))
    lost_hard = [(t, i) for t, i in lost_n if i in src_paired]
    lost_soft = [(t, i) for t, i in lost_n if i not in src_paired]
    new_hard = [(t, j) for t, j in new_n if write or j in res_paired]     # в write пары нет: бриф ≠ текст
    new_soft = [(t, j) for t, j in new_n if not (write or j in res_paired)]
    if lost_hard:
        out.append(Finding("A", "A3", "Имена, названия, редкие слова: потеряны", "hard",
                           ", ".join(f"«{t}»" for t, _ in lost_hard[:10]),
                           src_sents([i for _, i in lost_hard]),
                           "Вернуть имена, названия, аббревиатуры и авторские слова, которых нет в словаре."))
    if lost_soft:
        out.append(Finding("A", "A3", "Имена, названия, редкие слова: не найдены", "note",
                           ", ".join(f"«{t}»" for t, _ in lost_soft[:10])
                           + " — фраза переписана целиком, сверь глазами: синоним, однокоренное слово или потеря",
                           src_sents([i for _, i in lost_soft]), "Имена и названия исходника — на месте.",
                           counted=False))
    if new_hard:
        out.append(Finding("A", "A3", "Имена, названия, редкие слова: новые", "hard",
                           ", ".join(f"«{t}»" for t, _ in new_hard[:10]),
                           res_sents([i for _, i in new_hard]), "Не добавлять деятелей и названия, которых нет в исходнике."))
    if new_soft:
        out.append(Finding("A", "A3", "Имена, названия, редкие слова: новые во фразе без пары", "note",
                           ", ".join(f"«{t}»" for t, _ in new_soft[:10])
                           + " — у фразы нет пары в исходнике, сверь глазами: синоним или выдуманное имя",
                           res_sents([i for _, i in new_soft]), "Не добавлять деятелей и названия, которых нет в исходнике.",
                           counted=False))
    if write:
        return out
    # --- отрицания
    sp, rp = neg_pairs(src), neg_pairs(res)
    lost_pairs, flip_ids, compensated = _neg_lost(src, res, sp, rp, al, al_best)
    flips = []
    for i, j, text in flip_ids:
        flips.append(Frag("исходник", trim(src.sents[i].raw), text))
        flips.append(Frag("результат", trim(res.sents[j].raw), "без отрицания"))
    # зеркально: отрицание появилось при слове, которое в исходнике стояло без него («отвечает» → «не отвечает»)
    ral, ral_best = alignment(res, src)
    _, added_ids, _ = _neg_lost(res, src, rp, sp, ral, ral_best)
    for j, i, text in added_ids:
        flips.append(Frag("исходник", trim(src.sents[i].raw), "без отрицания"))
        flips.append(Frag("результат", trim(res.sents[j].raw), text))
    if flips:
        out.append(Finding("A", "A4", "Отрицание: смысл перевёрнут", "hard",
                           "слово осталось, а отрицание при нём пропало или появилось", flips[:MAX_FRAGS],
                           "Вернуть полярность исходника."))
    if pv is not None and lost_pairs and all(m_sent(i) for _, i in lost_pairs):
        for t, i in lost_pairs:
            clean(f"отрицание «{t}»", i)
        lost_pairs = []
    if len(rp) + compensated < len(sp) and lost_pairs:
        out.append(Finding("A", "A4", "Отрицания: стало меньше", "hard",
                           f"было {len(sp)}, стало {len(rp)}; пропали: " + ", ".join(f"«{t}»" for t, _ in lost_pairs[:6]),
                           src_sents([i for _, i in lost_pairs]),
                           "Каждое «не / нет / ни / никогда / нельзя» исходника должно остаться (кроме снятого «не просто X, а Y»)."))
    # --- модальность
    for name, pat in MODAL_CLASSES.items():
        a, b = modal_hits(src, pat), modal_hits(res, pat)
        if len(a) == len(b):
            continue
        what = "потеряна" if len(b) < len(a) else "добавлена"
        frs = []
        if len(b) < len(a):
            # где именно пропало: во фразе исходника модальных слов больше, чем в лучшей выровненной фразе результата
            ca, cb = Counter(i for i, _ in a), Counter(j for j, _ in b)
            lost_i = ([i for i in ca if al_best[i] is None or ca[i] > cb.get(al_best[i], 0)]
                      or [i for i, _ in a if not (al[i] & set(cb))] or [i for i, _ in a])
            if pv is not None and all(m_sent(i) for i in lost_i):
                for i in dict.fromkeys(lost_i):
                    clean(f"модальность «{', '.join(m for k, m in a if k == i)}»", i)
                continue
            for i in list(dict.fromkeys(lost_i))[:2]:
                frs.append(_fr("исходник", src.sents[i].raw, ", ".join(m for k, m in a if k == i)))
                if al_best[i] is not None:
                    frs.append(_fr("результат", res.sents[al_best[i]].raw))
        else:
            a_s = {i for i, _ in a}
            new_j = [j for j, _ in b if not (ral[j] & a_s)] or [j for j, _ in b]
            frs = [_fr("результат", res.sents[j].raw, ", ".join(m for k, m in b if k == j))
                   for j in list(dict.fromkeys(new_j))[:MAX_FRAGS]]
        out.append(Finding("A", "A5", f"Модальность {what}: {name}", "hard",
                           f"в исходнике {len(a)} ({', '.join(sorted({m for _, m in a})) or '—'}), "
                           f"в результате {len(b)} ({', '.join(sorted({m for _, m in b})) or '—'})",
                           frs[:MAX_FRAGS],
                           "Модальность — часть факта: «надо» не превращать в «можно», «стоит» или повелительное; "
                           "«позволит сократить» → «может сократить», а не «сократит»."))
    # --- вид и время
    if tk.has_morph():
        sv, rv = finite_verbs(src), finite_verbs(res)
        pool = Counter((v["lemma"], v["tense"]) for v in rv)
        unmatched_src = []
        for v in sv:
            k = (v["lemma"], v["tense"])
            if pool[k] > 0:
                pool[k] -= 1
            else:
                unmatched_src.append(v)
        free = []                                   # глаголы результата без пары в исходнике
        for v in rv:
            k = (v["lemma"], v["tense"])
            if pool[k] > 0:
                free.append(v)
                pool[k] -= 1
        # жёстко — только внутри выровненной пары фраз (общие леммы); в соседней фразе окна — подсказка
        #     (DEV-замер v2, P9: на контроле-пересказе A6 давало 9 находок, в основном между разными фразами)
        paired: dict[int, set] = {}
        for i, j in pairs:
            paired.setdefault(i, set()).add(j)
        changes, loose = [], []
        asp = {"perf": "сов.", "impf": "несов."}
        for v in unmatched_src:
            strong = paired.get(v["sent"], set())
            for sents, bucket in ((strong, changes), (al[v["sent"]] - strong, loose)):
                cand = [r for r in free if r["sent"] in sents]
                same = [r for r in cand if r["lemma"] == v["lemma"] and r["tense"] != v["tense"]]
                if same and "subj" in (v["tense"], same[0]["tense"]):
                    free.remove(same[0])   # «который настроит» → «чтобы настроил»: наклонение, а не время
                    break
                if same and v["tense"] is not None and same[0]["tense"] is not None:
                    r = same[0]
                    free.remove(r)
                    bucket.append((f"время: «{v['word']}» ({TENSE_RU[v['tense']]}) → «{r['word']}» "
                                   f"({TENSE_RU[r['tense']]})", v["sent"], r["sent"]))
                    break
                part = [r for r in cand if r["aspect"] and v["aspect"] and r["aspect"] != v["aspect"]
                        and _aspect_partners(r["lemma"], v["lemma"])]
                if part:
                    r = part[0]
                    free.remove(r)
                    bucket.append((f"вид: «{v['word']}» ({asp[v['aspect']]}) → «{r['word']}» ({asp[r['aspect']]})",
                                   v["sent"], r["sent"]))
                    break
        for found, sev in ((changes, "hard"), (loose, "note")):
            if not found:
                continue
            frs = []
            for _, i, j in found[:2]:
                frs += [_fr("исходник", src.sents[i].raw), _fr("результат", res.sents[j].raw)]
            msg = "; ".join(c for c, _, _ in found[:5])
            if sev == "note":
                msg += " — в соседней, а не в парной фразе: сверь глазами, та ли это мысль"
            out.append(Finding("A", "A6", "Вид или время глагола изменились" if sev == "hard"
                               else "Вид или время глагола: возможно, изменились", sev, msg, frs,
                               "«жду» ≠ «ждал», «выполняли» ≠ «выполнили»: вид и время брать из исходника.",
                               counted=sev == "hard"))
    # --- перечни
    res_keys = tk.all_keys(res)
    missing = []
    for items in block_lists(src):
        for it in items:
            if not _item_present(it, res_keys):
                missing.append((it, None))
    for i, items in inline_lists(src):
        if _evaluative(items):
            continue
        for it in items:
            if not _item_present(it, res_keys):
                missing.append((it, i))
    if pv is not None:
        for it, i in [(it, i) for it, i in missing if not _item_present(it, pv.keys)]:
            clean(f"пункт «{trim(it, 40)}»", i)
        missing = [(it, i) for it, i in missing if _item_present(it, pv.keys)]
    if missing:
        frs = [_fr("исходник", src.sents[i].raw if i is not None else it, it) for it, i in missing[:MAX_FRAGS]]
        out.append(Finding("A", "A7", "Перечень: пропали пункты", "hard",
                           "нет в результате: " + "; ".join(f"«{trim(it, 50)}»" for it, _ in missing[:8]), frs,
                           "Число пунктов любого перечня то же; менять можно только оформление."))
    # число пунктов сверяется у пары «список исходника — список результата с тем же содержанием», а не по порядку:
    # новая нумерация рубрик («Первое.» → «1.») — не тот же список (DEV-замер v2, P8)
    diffs = []
    rl = block_lists(res)
    used = set()
    for a in block_lists(src):
        best, best_k = 0.0, None
        for k, b in enumerate(rl):
            if k in used:
                continue
            bk = set().union(*[{v for t in _item_toks(x) for v in tk.tok_variants(t)} for x in b])
            share = sum(_item_present(it, bk) for it in a) / len(a)
            if share > best:
                best, best_k = share, k
        if best_k is not None and best >= 0.5:
            used.add(best_k)
            if len(rl[best_k]) != len(a):
                diffs.append((len(a), len(rl[best_k])))
    if diffs:
        out.append(Finding("A", "A7", "Перечень: другое число пунктов", "hard",
                           "; ".join(f"было {a}, стало {b}" for a, b in diffs),
                           hint="Число пунктов перечня сохранить."))
    # --- «а не Y»
    lost_ane = []
    for i, s in enumerate(src.sents):
        ws = s.words
        for j in range(len(ws) - 1):
            if not (ws[j].low == "а" and ws[j + 1].low == "не"):
                continue
            y = _next_content(ws, j + 1) or (ws[j + 2] if j + 2 < len(ws) else None)
            if y is None:
                continue
            var = tk.tok_variants(y)
            ok = any(any(tk.tok_variants(t) & var for t in rs.words) and any(t.low in NEG_LIKE for t in rs.words)
                     for rs in res.sents)
            if not ok:
                lost_ane.append((f"а не {y.text}", i))
    if pv is not None:
        for t, i in [(t, i) for t, i in lost_ane if m_sent(i)]:
            clean(f"«{t}»", i)
        lost_ane = [(t, i) for t, i in lost_ane if not m_sent(i)]
    if lost_ane:
        out.append(Finding("A", "A8", "Граница «а не Y» пропала", "hard",
                           ", ".join(f"«{t}»" for t, _ in lost_ane),
                           src_sents([i for _, i in lost_ane]),
                           "«а не Y» задаёт охват утверждения: отрицаемый полюс должен остаться."))
    # --- длина
    lo, hi = BUDGETS["diff"]["length_ratio"]
    m_cut = prov is not None and prov.m_cut and mode == "rewrite"
    v5 = prov is not None and prov.no_source and mode == "rewrite" and bool(prov.v5)
    if m_cut and not v5:
        lo = BUDGETS["diff"].get("length_ratio_m_cut", 0.70)     # вырезано М: рамка промо, мораль, повторы (v4)
    src_n, res_n = src.n_words, res.n_words
    if v5 and src.n_words:
        # v5 без источника: сократить не больше чем на 10% слов, и только за счёт рамки модели. Нижняя граница
        # считается от черновика без рамки (строка-заголовок, снятые фразы М, слова формул, шаблонов и эпитетов),
        # верхняя — от черновика без снятых фраз М (перенесённый в текст заголовок — не дописанное).
        lo = 1 - V5_SHORTEN_MAX
        src_lo = max(1, src.n_words - prov.v5.get("frame_words", 0))
        src_hi = max(1, src.n_words - prov.v5.get("removed_words", 0))
        short, long_ = res_n / src_lo < lo, res_n / src_hi > hi
        if short or long_:
            n_ref = src_lo if short else src_hi
            out.append(Finding("A", "A9", f"Длина вне {lo * 100:.0f}–{hi:.0%} (без источника)", "hard",
                               f"{res_n} слов против {n_ref} в черновике без "
                               + ("рамки модели" if short else "снятых фраз М") + f" ({res_n / n_ref:.0%})",
                               hint="Без источника сокращать не больше чем на 10% и только за счёт рамки модели "
                                    "(формулы, обёртка, повторы, строка-заголовок); фразы с содержанием "
                                    "упрощать, а не удалять. Каждую снятую фразу перечислить в заметке."))
    elif src_n:
        ratio = res_n / src_n
        if not lo <= ratio <= hi:
            out.append(Finding("A", "A9", f"Длина вне {lo * 100:.0f}–{hi:.0%}", "hard",       # как в v3: «85–115%»
                               f"{res.n_words} слов против {src.n_words} в исходнике ({ratio:.0%})"
                               + ("; нижняя граница 70%: из черновика вырезаны фразы М" if m_cut else ""),
                               hint="Не пересказывать и не дописывать; вернуть выпавшее или убрать добавленное."))
    # --- знаменательные слова: подсказка, не нарушение. На DEV-замере (контроль-пересказ) A10 сработало
    #     в 19 текстах, из них 12 — без ошибок по ручной сверке; во всех 7 текстах с ошибками есть другие
    #     находки A, а места ошибки A10 не показывает
    sk = set()
    for s in src.sents:
        sk |= tk.content_keys(s.words)
    if sk:
        kept = len([k for k in sk if k in res_keys]) / len(sk)
        thr = BUDGETS["diff"]["lemma_retention_min"]
        if kept < thr:
            lost_k = sorted(k for k in sk if k not in res_keys)[:15]
            out.append(Finding("A", "A10", "Знаменательных слов исходника меньше 75%", "note",
                               f"сохранено {kept:.0%}; нет, например: " + ", ".join(lost_k)
                               + " — похоже на пересказ, сверь смысл глазами",
                               hint="Править точечно, а не пересказывать.", counted=False))
    # --- рамки мнения и источники
    frames = _frames_lost(src, res, al)
    if pv is not None:
        by_text = {trim(s.raw): i for i, s in enumerate(src.sents)}
        keep = []
        for f in frames:
            ids = [by_text.get(fr.text) for fr in f.frags if fr.where == "исходник"]
            if ids and all(m_sent(i) for i in ids):
                for i in ids:
                    clean(f"рамка «{f.frags[0].match or f.title}»", i)
            else:
                keep.append(f)
        frames = keep
    out += frames
    # --- цитаты: текст в кавычках исходника — дословно (pikabu-26 на контроле: «солидного веса» → «солидной
    #     комплекции» не ловилось ничем)
    changed = quotes_changed(src, res)
    if pv is not None:
        ref_norm = tk.fold_yo(pv.ref.text.lower())
        for q, i in [(q, i) for q, i in changed if tk.fold_yo(q.lower()) not in ref_norm]:
            clean(f"цитата «{trim(q, 40)}»", i)
        changed = [(q, i) for q, i in changed if tk.fold_yo(q.lower()) in ref_norm]
    if changed:
        frs = []
        for q, i in changed[:2]:
            frs.append(_fr("исходник", src.sents[i].raw if i is not None else q, q))
            if i is not None and al_best[i] is not None:
                frs.append(_fr("результат", res.sents[al_best[i]].raw))
        out.append(Finding("A", "A12", "Цитата изменена", "hard",
                           "нет в результате дословно: " + "; ".join(f"«{trim(q, 60)}»" for q, _ in changed[:6]),
                           frs[:MAX_FRAGS],
                           "Текст в кавычках — чужие слова или название: вернуть дословно, править можно только вокруг."))
    return out


# =============================================================================== B: след правки
# след правки сверяется с исходником, поэтому здесь шире, чем бюджеты C (CORE-05, CORE-06):
# любая новая рамка мнения или «честно» — это дописанное от себя.
# Источники («по моему опыту», «по их данным») — не рамка позиции, а часть факта: у них своё правило «source».
PERSONA_RX = (r"\bпо-моему\b|\bна мой взгляд\b|\bя (?:считаю|уверен|уверена|убежден|убеждена)\b|"
              r"справедливости ради|\bмне кажется\b|\bкак по мне\b|\bс моей точки зрения\b|\bя думаю\b|^\W*думаю,|"
              r"\bлично я\b|\bпо-моему мнению\b|\bпо моему мнению\b|\bя бы сказал\b")
COMMA_AND_RX = r",\s*(?:и|а)\b(?!\s+т\.\s?[дп])"
# «X, что Y» на месте двоеточия. Рамка мнения «уверен» считается вместе с формой «уверен:», поэтому
# рекомендованная замена «Я уверен: X» → «Я уверен, что X» не новая; «понял / сказали / признаюсь, что»
# считаются без двоеточия: «Мне сказали: X» → «Мне сказали, что X» — тоже след правки (DEV-замер v2, P3)
UVEREN_CHTO_RX = (r"\b(?:уверен|уверена|уверены|убежден|убеждена|убеждены)(?:\s*:|,?\s+что\b)"
                  r"|\b(?:понял|поняла|поняли|понимаю|понимаем|признаюсь|признаемся|признался|призналась|признались|"
                  r"сказали)\s*,?\s+что\b")
# рамка мнения или источник, приклеенные к фразе через союз: «…, и, как мне кажется, …» (P4)
_FRAME_START = (r"как\s+(?:мне|нам)\s+(?:кажется|казалось|думается)|(?:мне|нам)\s+(?:кажется|казалось|думается)"
                r"|по-моему|по-нашему|на\s+(?:мой|наш)\s+взгляд|как\s+по\s+мне|с\s+(?:моей|нашей)\s+точки\s+зрения"
                r"|по\s+(?:моему|нашему)\s+(?:мнению|опыту|убеждению|ощущению|наблюдениям|данным|подсчетам)"
                r"|по\s+(?:их|его|ее)\s+(?:мнению|данным|словам|оценкам?|подсчетам|наблюдениям)"
                r"|по\s+(?:данным|словам|мнению|оценкам?)\s+[^\W\d_]"
                r"|(?:я\s+)?(?:уверен|уверена|убежден|убеждена|считаю|думаю|полагаю)\b"
                r"|(?:мы\s+)?(?:уверены|убеждены|считаем|думаем|полагаем)\b"
                r"|как\s+(?:пишет|пишут|считает|считают|говорит|говорят|сообщает|сообщают|отмечает|отмечают)\b")
FRAME_GLUED_RX = rf",\s*(?:и|а|но)\s*,?\s*(?:—\s*)?(?:{_FRAME_START})"
# рубрики «Первое: … Второе: …» и «во-первых»: в нумерованный список их превращать можно (SKILL v3, правило 2)
ORDINAL_RUBRIC_RX = re.compile(
    r"^\W*(?:(?:перв|втор|трет|четверт|пят|шест|седьм|восьм|девят|десят)(?:ое|ая|ый|ий|ой|ье)"
    r"|во-первых|во-вторых|в-третьих|в-четвертых|в-пятых)\s*[.:,—–-]", re.I)


def ordinal_rubric_hits(doc: tk.Doc) -> list[Hit]:
    return [Hit(s.raw, s.norm.strip()[:20]) for s in doc.sents if ORDINAL_RUBRIC_RX.match(s.norm)]
HONESTY_RX = (r"\bчестно говоря\b|\bесли честно\b|\bпризнаюсь честно\b|\bскажу честно\b|^\W*Честно[,?]|"
              r"\bбуду чест(?:ен|на)\b|\bчестно (?:скажу|признаюсь|признаться|сказать)\b|"
              r"[,—(]\s*честно\s*(?:[,—)!?.]|$)|\bоткровенно говоря\b|\bположа руку на сердце\b|\bскажу как есть\b")
TY_RX = r"\b(?:ты|тебя|тебе|тобой|тобою|твой|твоя|твое|твои|твоего|твоей|твоему|твоим|твоими|твоих|твою|твоем)\b"


def _rhet_q(doc: tk.Doc) -> list[Hit]:
    out = []
    for p in doc.paras:
        for a, b in zip(p, p[1:]):
            sa, sb = doc.sents[a], doc.sents[b]
            if sa.raw.rstrip().endswith("?") and not sb.raw.rstrip().endswith("?"):
                out.append(Hit(sa.raw, "?"))
    return out


def trace(doc: tk.Doc) -> dict[str, list[Hit]]:
    t: dict[str, list[Hit]] = {}
    t["colon"] = colon_hits(doc, {"label", "reveal", "list", "speech", "service", "end"})
    t["semicolon_eol"] = regex_hits(doc, "line", r";\s*$")
    t["dash_turn"] = regex_hits(doc, "sentence", r"\s—\s+(?:и|а|но)\b")
    t["label"] = colon_hits(doc, {"label"})
    t["reveal"] = colon_hits(doc, {"reveal"})
    t["label_reveal"] = colon_hits(doc, {"label", "reveal"})
    for key, pat in (("naprimer", r"—\s*например"), ("odnako", r"\bоднако\b"), ("imenno", r"\bименно\b"),
                     ("lish", r"\bлишь\b|\bисключительно\b"), ("blagodarya", r"\bблагодаря\b"),
                     ("zametno", r"\bзаметно\b"), ("klyuchevoy", r"\bключев\w+"), ("prostoy_colon", r"\bпрост\w*\s*:"),
                     ("ya_uveren_colon", r"\bя (?:уверен|уверена|убежден|убеждена)\s*:"),
                     ("persona", PERSONA_RX), ("honesty", HONESTY_RX),
                     ("nado", r"\b(?:надо|необходимо|должен|должна|должно|должны)\b"),
                     ("causal", r"\bпотому что\b|\bтак как\b"), ("ochen", r"\bочень\b"),
                     ("to_est", r"\bто есть\b|\bи т\.\s?[дп]\."), ("ty", TY_RX),
                     # новые маркеры скилла (DEV-замер, P3 и P4)
                     ("comma_and", COMMA_AND_RX), ("potomu_new", r"\bпотому что\b"),
                     ("v_tom", r"\bв том,?\s+(?:что|чтобы)\b"),
                     ("vo_pervyh", r"\bво-первых\b|\bво-вторых\b|\bв-третьих\b|\bв-четвертых\b"),
                     ("uveren_chto", UVEREN_CHTO_RX),
                     # DEV-замер v2: «так что» (P3) и рамка, приклеенная через «, и,» (P4)
                     ("tak_chto", r"\bтак что\b"), ("frame_glued", FRAME_GLUED_RX)):
        t[key] = regex_hits(doc, "sentence", pat)
    # ярлык двоеточия, оставленный короткой фразой: «Суть простая. Первым гасится…» (P1)
    t["label_sent"] = [Hit(doc.sents[i].raw, doc.sents[i].raw.strip()) for i in range(len(doc.sents))
                       if tk.label_sentence(doc, i)]
    t["source"] = [Hit(doc.sents[i].raw, m) for i, m in frame_hits(doc).get("источник", [])]
    # для исходника — и мягкие формы: «Аналитик сказал, что…» → «По словам аналитика…» — источник не новый
    t["source_any"] = [Hit(doc.sents[i].raw, m) for i, m in frame_hits(doc, strict=False).get("источник", [])]
    t["conj_chain"] = [Hit(s.raw, f"{n} союза") for s in doc.sents for n in [tk.coord_conj_count(s)] if n > 2]
    if tk.has_morph():
        t["comma_splice"] = [Hit(s.raw, f) for s in doc.sents for f in tk.comma_splices(s)]
        t["comma_splice_any"] = [Hit(s.raw, f) for s in doc.sents for f in tk.comma_splices(s, after_colon=True)]
    lw = BUDGETS["rhythm"]["long_words"]
    t["long"] = [Hit(s.raw, f"{s.n_words} слов") for s in doc.sents if s.n_words > lw]
    t["particles"] = [Hit(s.raw, p) for s in doc.sents for p in tk.particles(s)]
    t["rhet_q"] = _rhet_q(doc)
    t["questions"] = [Hit(s.raw, "?") for s in doc.sents if s.raw.rstrip().endswith("?")]
    if tk.has_morph():
        t["my_verbs"] = [Hit(s.raw, w.text) for s in doc.sents for w in s.words
                         if w.w and w.w.pos == "VERB" and ("incl" in w.w.tags or ("1per" in w.w.tags and "plur" in w.w.tags))]
    t["paren"] = [Hit(s.raw, "(") for s in doc.sents for _ in re.finditer(r"\((?=[^\s)(])", s.norm)]
    t["ellipsis_smiley"] = [Hit(s.raw, m.group(0)) for s in doc.sents
                            for m in re.finditer(r"\.{3,}|\){2,}|\({2,}|[:;]-?[)(]|\?!|!\?", s.norm)]
    t["excl"] = [Hit(s.raw, "!") for s in doc.sents for _ in range(s.norm.count("!"))]
    t["emoji"] = [Hit(raw, e) for raw, _ in doc.lines for e in tk.EMOJI_RX.findall(raw)]
    t["structure"] = structure_hits(doc)
    if doc.has_paragraphs and len(doc.paras) >= 2:
        t["one_sent_paras"] = [Hit(doc.sents[p[0]].raw, "") for p in doc.paras if len(p) == 1]
    return t


# (ключ, направление, название, подсказка)
B_RULES = [
    ("colon", "more", "Двоеточий больше, чем в исходнике (+1 на 300 слов)",
     "Чистка одного маркера рождает другой: вернуть фразы без новых «:»."),
    ("semicolon_eol", "more", "Новые «;» в конце строк", "«;» не добавлять; пункт кончается точкой или ничем."),
    ("dash_turn", "more", "Новые тире-повороты «— и / — а / — но»", "Союз без тире: «, и …»."),
    ("label", "more", "Новые ярлыки с двоеточием", "Ярлыков не больше, чем в исходнике."),
    ("reveal", "more", "Новые двоеточия-раскрытия («Причина проста: …»)",
     "Двоеточие-раскрытие и ярлык не вставлять: развернуть союзом, который был в исходнике, или вернуть фразу."),
    ("naprimer", "more", "Новое «— например»", "Лексический след ИИ-правки (×7,8): не вставлять."),
    ("odnako", "more", "Новое «однако»", "Не вставлять: след правки."),
    ("imenno", "more", "Новое «именно»", "Не вставлять: след правки."),
    ("lish", "more", "Новое «лишь / исключительно»", "Не вставлять: след правки."),
    ("blagodarya", "more", "Новое «благодаря»", "Не вставлять: след правки."),
    ("zametno", "more", "Новое «заметно»", "Не вставлять: след правки."),
    ("klyuchevoy", "more", "Новое «ключевой»", "Не вставлять: след правки."),
    ("prostoy_colon", "more", "Новое «простой:»", "Не вставлять: след правки."),
    ("ya_uveren_colon", "more", "Новое «Я уверен:»", "Не вставлять: след правки."),
    ("persona", "more", "Новые «по-моему / мне кажется / я считаю / я уверен»", "Мнения только из слов автора."),
    ("source", "more", "Новые источники и опыт («по моему опыту», «по их данным»)",
     "Источник, опыт и чужое мнение — только из слов автора."),
    ("honesty", "more", "Новое «честно»", "«Честно» только из слов автора."),
    ("comma_and", "more", "Новые «, и» / «, а» (больше +1 на 200 слов)",
     "Склейка через «, и» / «, а» сама становится маркером (у людей «, и» около 1 на 1000 слов): склеивать "
     "через «который», «когда», «если», причастный оборот или оставить две фразы."),
    ("comma_splice", "more", "Новая склейка через запятую (две самостоятельные фразы)",
     "Две самостоятельные фразы не соединять одной запятой: вернуть точку или союз того отношения, что было."),
    ("conj_chain", "more", "Новая цепочка: больше двух сочинительных союзов во фразе",
     "Одна склейка — одно соединение: во фразе не больше двух «и / а / но»; лучше подчинение («который», «когда»)."),
    ("potomu_new", "more", "Новые «потому что» (больше +1 на 300 слов)",
     "Двоеточие по умолчанию снимать вместе с ярлыком и оставлять раскрытие («Причина проста: X.» → «X.»); "
     "«потому что» — только если причина есть в исходнике."),
    ("tak_chto", "more", "Новые «так что» (больше +1 на 300 слов)",
     "«так что» — третий одноразовый заменитель двоеточия после «потому что» и «, и» (у людей DEV — 0): "
     "снять ярлык и оставить раскрытие или оставить двоеточие в пределах бюджета жанра."),
    ("v_tom", "more", "Новые «X в том, что / чтобы» (больше одного)",
     "«Суть в том, что» не больше одного нового на текст: чаще снять ярлык и оставить раскрытие («Суть проста: X.» → «X.»)."),
    ("vo_pervyh", "more", "Новые «во-первых / во-вторых»",
     "Рубрики «Первое: … Второе: …» не превращать в «во-первых»: простой нумерованный список или без нумерации."),
    ("uveren_chto", "more", "Новые «уверен / понял / сказали / признаюсь, что» (больше одного)",
     "«X: Y» → «X, что Y» — тоже маркер правки (у людей DEV — 0): не больше одного нового на текст. Вводный глагол "
     "(«Сразу признаюсь:», «Мне сказали:») лучше убрать или оставить двоеточие в пределах бюджета. "
     "«Я уверен: X» → «Я уверен, что X» допустимо всегда."),
    ("label_sent", "more", "Ярлык стал отдельной фразой («Суть простая.», «Сцена знакомая.»)",
     "Тот же ход «ярлык → раскрытие», только рубленый: снять ярлык и оставить раскрытие («Суть простая: X.» → «X.»). "
     "Если ярлык что-то утверждает («Метод щадящий: прогресс виден сразу»), поставить союз того отношения, что было, "
     "или перестроить с подчинением."),
    ("frame_glued", "more", "Рамка мнения или источник приклеены через союз («…, и, как мне кажется, …»)",
     "Фраза, которая начинается с рамки («Мне кажется…», «По моему опыту…»), остаётся отдельной: вернуть точку."),
    ("excl", "more", "Новые «!»", "«!» не вставлять."),
    ("emoji", "more", "Новые эмодзи", "Эмодзи не вставлять."),
    ("ellipsis_smiley", "more", "Новые многоточия, «))», «?!»", "Фальшивую интонацию не вставлять."),
    ("questions", "more", "Новые вопросы", "Вопросы к читателю только из источника."),
    ("structure", "more", "Новая разметка, пункты, «Шаг N»", "Списки, рубрики и заголовок — только если они были."),
    ("long", "less", "Длинных фраз (> 25 слов) стало меньше 70% исходника", "Длинные фразы автора не дробить."),
    ("particles", "less", "Пропали частицы («же, ведь, вот, ну, -то»)", "Частицы автора не удалять."),
    ("nado", "less", "Пропали «надо / необходимо / должен»", "Не заменять на «нужно / стоит / можно» и не переводить в повелительное."),
    ("causal", "less", "Пропали «потому что / так как»", "Причинные союзы автора не удалять."),
    ("ochen", "less", "Пропало «очень»", "Не менять на «крайне / действительно»."),
    ("to_est", "less", "Пропали «то есть / и т. д.»", "Не удалять: несут уточнение и открытый перечень."),
    ("rhet_q", "less", "Пропали риторические вопросы", "Вопрос не превращать в утверждение."),
    ("ty", "less", "Пропало обращение на «ты»", "Форма обращения — как в исходнике."),
    ("my_verbs", "less", "Пропало инструктивное «мы» («открываем, жмём»)", "Не переводить «мы» в «Откройте»."),
    ("paren", "less", "Скобок стало меньше 80% исходника", "Авторские скобки-ремарки не удалять."),
    ("ellipsis_smiley", "less", "Пропали многоточия, «))», «?!» автора", "Сохранять."),
    ("one_sent_paras", "less", "Однофразных абзацев стало меньше", "Однофразные абзацы автора не склеивать."),
]


def _dash_glyphs(text: str) -> Counter:
    c = Counter()
    for line in text.split("\n"):
        body = re.sub(r"^\s*[-–—]\s", "", line)          # реплика или пункт в начале строки
        c["«—»"] += len(re.findall(r"[—―]", body))
        c["«–»"] += len(re.findall(r"(?<=\s)–(?=\s)", body))
        c["« - »"] += len(re.findall(r"(?<=\S)[ \t]-[ \t](?=\S)", body))
        c["«--»"] += len(re.findall(r"(?<!-)--(?!-)", body))
    return c


def _range_glyphs(text: str) -> Counter:
    return Counter({"«5-7»": len(re.findall(r"\d-\d", text)), "«5–7»": len(re.findall(r"\d\s?[–—]\s?\d", text))})


def _quote_styles(text: str) -> Counter:
    return Counter({"«ёлочки»": len(re.findall(r"[«»]", text)), "прямые \"": text.count('"'),
                    "“лапки”": len(re.findall(r"[“”„]", text))})


def _new_kinds(src_c: Counter, res_c: Counter) -> list[str]:
    s_k = {k for k, v in src_c.items() if v}
    r_k = {k for k, v in res_c.items() if v}
    return sorted(r_k - s_k) if s_k else []


def _glyph_frags(doc: tk.Doc, pattern: str) -> list[Frag]:
    r = re.compile(pattern)
    return [_fr("результат", s.raw, m.group(0)) for s in doc.sents for m in r.finditer(s.raw)][:MAX_FRAGS]


def _md_free(doc: tk.Doc) -> tk.Doc:
    t = tk.strip_markdown(doc.text)
    return doc if t == doc.text else tk.Doc(t)


def _headless(doc: tk.Doc, heads: set) -> tk.Doc:
    """Текст без строк-заголовков и без markdown."""
    t = tk.strip_markdown(tk.strip_md_headers(doc.text, heads))
    return doc if t == doc.text else tk.Doc(t)


# --------------------------------------------------------------- средняя фраза (P2 DEV-замера v2)
def _kept_lengths(a: tk.Doc, b: tk.Doc) -> list[tuple[int, int]]:
    """(номер, длина) фраз a, которые уцелели в b (не меньше половины знаменательных лемм есть в b).
    Удалённые обёртка и хвост («Если хотите, могу…») и фразы без знаменательных слов («Удачи!») не считаются."""
    bk = set()
    for s in b.sents:
        bk |= tk.content_keys(s.words)
    out = []
    for i, s in enumerate(a.sents):
        k = tk.content_keys(s.words)
        if k and len(k & bk) * 2 >= len(k):
            out.append((i, s.n_words))
    return out


def mean_drop(src: tk.Doc, res: tk.Doc) -> tuple[float, float, list[int]] | None:
    """(средняя фраза исходника, результата, фразы исходника, поделённые на две и больше), если результат
    короче исходника больше чем на mean_drop_max (10%) и хотя бы на 0,5 слова. В исходнике — только фразы,
    которые уцелели в результате; нужно не меньше 3 фраз и 40 слов."""
    d = BUDGETS["diff"]
    sk = _kept_lengths(src, res)
    rk = [s.n_words for s in res.sents if tk.content_keys(s.words)]
    if len(sk) < d.get("mean_drop_min_sents", 3) or sum(n for _, n in sk) < d.get("mean_drop_min_words", 40) or not rk:
        return None
    sm = sum(n for _, n in sk) / len(sk)
    rm = sum(rk) / len(rk)
    if rm >= sm * (1 - d.get("mean_drop_max", 0.10)) or sm - rm < 0.5:
        return None
    return sm, rm, split_sentences(src, res)


def split_sentences(src: tk.Doc, res: tk.Doc) -> list[tuple[int, list[int]]]:
    """Фразы исходника, поделённые в результате: подряд идут две и больше фразы результата, у каждой не меньше
    60% знаменательных лемм из этой фразы исходника, вместе они покрывают не меньше 60% её лемм, и ни одна
    в одиночку не покрывает 80%."""
    rk = [tk.content_keys(s.words) for s in res.sents]
    out = []
    for i, s in enumerate(src.sents):
        k = tk.content_keys(s.words)
        if len(k) < 3:
            continue
        inside = [j for j, kj in enumerate(rk) if kj and len(kj & k) * 5 >= len(kj) * 3]
        run: list[int] = []
        for j in inside + [None]:
            if j is not None and run and j == run[-1] + 1:
                run.append(j)
                continue
            if len(run) >= 2:
                cov = set().union(*(rk[x] & k for x in run))
                if len(cov) * 5 >= len(k) * 3 and all(len(rk[x] & k) * 5 < len(k) * 4 for x in run):
                    out.append((i, run))
                    break
            run = [j] if j is not None else []
    return out


# --------------------------------------------------------------- новое тире на месте двоеточия или оборота (P5)
_TURN_LEMMAS = frozenset({"заключаться", "состоять"})
_TURN_STOP = frozenset({".", "!", "?", ";", "(", ")", "...", "…"})


def _what_follows(toks: list, k: int) -> str | None:
    """Что стоит в исходнике сразу за словом k: «:» (не время) через 0–2 слова — «двоеточие»; деепричастие,
    причастие или «заключается / состоит» в ближайших трёх словах — «оборот»; «—» — тире уже было."""
    words = 0
    for x in toks[k + 1:]:
        if not x.is_word:
            if x.text in ("—", "–"):
                return "тире"
            if x.text == ":":
                return "двоеточие" if words <= 2 else None
            if x.text in _TURN_STOP:
                return None
            continue
        words += 1
        if words > 3 or x.is_num:
            return None
        if x.low in tk.FROZEN_GRND:
            return None                 # «включая», «начиная с», «благодаря» — предлоги, а не оборот
        if x.w is not None and (x.w.pos in ("GRND", "PRTF") or x.w.lemma in _TURN_LEMMAS):
            return "оборот"
    return None


def new_dash_turns(src: tk.Doc, res: tk.Doc) -> list[Hit]:
    """Новое тире результата там, где в исходнике стояло двоеточие или оборот: «Моя идея заключается в
    создании…» → «Моя идея — создать…», «Причина проста: X» → «Причина проста — X», «ушёл, хлопнув дверью» →
    «ушёл — хлопнул дверью». Место ищется по слову перед тире во фразах исходника рядом с выровненной."""
    if not tk.has_morph():
        return []
    ral, ral_best = alignment(res, src)
    out = []

    def prose_dashes(sent: tk.Sent) -> int:
        return sum(c not in tk.NON_PROSE_DASH for c in tk.classify_dash_sentence(sent.norm, sent.line_start)) \
            if "—" in sent.norm else 0

    for j, s in enumerate(res.sents):
        if "—" not in s.norm or not ral[j]:
            continue
        classes = tk.classify_dash_sentence(s.norm, s.line_start)
        if sum(c not in tk.NON_PROSE_DASH for c in classes) <= prose_dashes(src.sents[ral_best[j]]):
            continue                    # тире не прибавилось: «Задача, стоящая перед нами, — успеть» → «Задача — успеть»
        for m, cl in zip(re.finditer("—", s.norm), classes):
            if cl in tk.NON_PROSE_DASH or cl == "paired":
                continue                # парное тире — вставка («пользователи — например, в Аргентине —»)
            before = s.norm[:m.start()]
            left = _wordlist(before)
            # слово стоит вплотную перед тире (через пробел или кавычку), справа не число: «изменённый: −50» —
            # это минус после двоеточия, а не тире на его месте
            if not left or not re.search(r"[^\W_][\"»)]?\s*$", before) or re.match(r"\s*\d", s.norm[m.end():]):
                continue
            anchor = tk.make_tok(left[-1])
            if not (tk.is_content(anchor) or anchor.is_num or anchor.is_latin):
                continue                # «…, и — Уверен»: служебное слово, его место в исходнике не найти
            var = tk.tok_variants(anchor)
            kinds = set()
            for i in sorted(ral[j]):
                toks = src.sents[i].toks
                for k, t in enumerate(toks):
                    if t.is_word and tk.tok_variants(t) & var:
                        kinds.add(_what_follows(toks, k))
            if "тире" in kinds:
                continue
            kind = "двоеточие" if "двоеточие" in kinds else "оборот" if "оборот" in kinds else None
            if kind:
                out.append(Hit(s.raw, f"{left[-1]} — (было: {kind})"))
    return out


def _b_slack(key: str, doc: tk.Doc) -> int:
    """Сколько новых срабатываний правила B допустимо: «:» +1 на 300 слов, «, и / , а» +1 на 200 слов,
    «потому что» и «так что» +1 на 300 слов, «X в том, что» и «уверен / понял / сказали, что» — одно на текст;
    остальное — ни одного."""
    d = BUDGETS["diff"]
    per = {"colon": d["colon_slack_per_words"], "comma_and": d.get("comma_and_slack_per_words", 200),
           "potomu_new": d.get("potomu_slack_per_words", 300),
           "tak_chto": d.get("tak_chto_slack_per_words", 300)}.get(key)
    if per:
        return max(1, math.ceil(doc.n_words / per))
    return d.get("fixed_slack", {"v_tom": 1, "uveren_chto": 1}).get(key, 0)


def block_b(src: tk.Doc, res: tk.Doc, mode: str, profile: str) -> list[Finding]:
    out: list[Finding] = []
    # --- типографика автора
    new_dash = _new_kinds(_dash_glyphs(src.text), _dash_glyphs(res.text))
    new_range = _new_kinds(_range_glyphs(src.text), _range_glyphs(res.text))
    if new_dash or new_range:
        pats = {"«—»": r"[—―]", "«–»": r"\s–\s", "« - »": r"\S\s-\s\S", "«--»": r"--", "«5–7»": r"\d\s?[–—]\s?\d",
                "«5-7»": r"\d-\d"}
        frs = [f for k in new_dash + new_range for f in _glyph_frags(res, pats[k])][:MAX_FRAGS]
        have = [k for k, v in (_dash_glyphs(src.text) + _range_glyphs(src.text)).items() if v]
        out.append(Finding("B", "B1", "Тире набрано другим знаком", "hard",
                           f"в исходнике {', '.join(have)}; в результате появилось {', '.join(new_dash + new_range)}",
                           frs, "Глиф тире брать из исходника: « - » не превращать в «—»."))
    new_q = _new_kinds(_quote_styles(src.text), _quote_styles(res.text))
    if new_q:
        pats = {"«ёлочки»": r"[«»]", "прямые \"": r'"', "“лапки”": r"[“”„]"}
        frs = [f for k in new_q for f in _glyph_frags(res, pats[k])][:MAX_FRAGS]
        out.append(Finding("B", "B2", "Кавычки другого вида", "hard", f"появились {', '.join(new_q)}", frs,
                           "Кавычки как в исходнике: прямые не менять на «ёлочки»."))
    src_yo = len(re.findall("[ёЁ]", src.text))
    res_yo = len(re.findall("[ёЁ]", res.text))
    src_with_yo, src_without_yo = yo_hits(src)  # «ещё» / «еще»: слова, которым «ё» положена
    if src_yo == 0 and res_yo > 0 and (src_without_yo or src.n_words >= 30):
        words = sorted({t.text for s in res.sents for t in s.words if "ё" in t.text.lower()})
        out.append(Finding("B", "B3", "Появилась «ё»", "hard",
                           f"в исходнике «ё» нет, в результате {res_yo}: " + ", ".join(words[:8]),
                           _glyph_frags(res, "[ёЁ]"), "«ё» не вводить в текст без «ё» (исключение — озвучка)."))
    elif src_yo > 0:
        # смешанную «ё» автора можно привести к той конвенции, которой в тексте больше (DEV-замер v2, P8:
        # opinion-134 — «её» при «еще», «нашел», «шел»), но не к меньшинству
        nw, nwo = len(src_with_yo), len(src_without_yo)
        majority_e = nwo > 0 and nwo >= nw
        majority_yo = nw > 0 and nw >= nwo
        yo_words = {tk.fold_yo(t.low) for s in src.sents for t in s.words if "ё" in t.text.lower()}
        dropped = sorted({t.text for s in res.sents for t in s.words
                          if "ё" not in t.text.lower() and t.low in yo_words})
        if dropped and res_yo == 0 and not majority_e:
            out.append(Finding("B", "B3", "«ё» убрана", "hard", "в исходнике «ё» была, в результате нет: "
                               + ", ".join(dropped[:8]),
                               hint="Конвенцию «ё» автора сохранить; убрать «ё» можно, только если без неё в тексте "
                                    "больше слов, чем с ней."))
        res_with = yo_hits(res)[0]
        if majority_e and not majority_yo and len(res_with) > nw:
            added = sorted({h.match for h in res_with} - {h.match for h in src_with_yo})
            out.append(Finding("B", "B3", "«ё» расставлена против конвенции автора", "hard",
                               f"в исходнике слов с «ё» {nw}, без «ё» {nwo}; в результате с «ё» {len(res_with)}: "
                               + ", ".join(added[:8]), _glyph_frags(res, "[ёЁ]"),
                               "Смешанную «ё» приводить к той конвенции, которой в тексте больше (здесь — без «ё»)."))
    # --- счётчики «не больше / не меньше исходника»; markdown снят с обеих сторон («**Что делать?**» и
    #     «Что делать?» — одна и та же фраза), новая разметка сверяется по исходному тексту (structure)
    sb, rb = _md_free(src), _md_free(res)
    ts, tr = trace(sb), trace(rb)
    # нумерованный список на месте рубрик «Первое: … Второе: …» — не новая разметка (SKILL v3, правило 2)
    ts["structure"] = structure_hits(src) + ordinal_rubric_hits(sb)
    tr["structure"] = structure_hits(res)
    # однофразные абзацы и средняя фраза — без строк-заголовков: снятый «## Позиция Facebook» — не потерянный
    # однофразный абзац (DEV-замер v2, P8), а оставленный строкой заголовок исходника не считается новым
    heads = tk.md_header_texts(src.text) | tk.md_header_texts(res.text)
    sh, rh = _headless(src, heads), _headless(res, heads)
    for d, doc in ((ts, sh), (tr, rh)):
        d.pop("one_sent_paras", None)
        if doc.has_paragraphs and len(doc.paras) >= 2:
            d["one_sent_paras"] = [Hit(doc.sents[p[0]].raw, "") for p in doc.paras if len(p) == 1]
    skip = set()
    if mode == "rewrite" and profile == "yandex":
        skip.add("rhet_q")          # у Алисы риторических вопросов вдвое больше людей (NT-12)
    for key, direction, title, hint in B_RULES:
        if key in skip or key not in ts or key not in tr:
            continue
        a, b = ts[key], tr[key]
        if key in ("source", "comma_splice"):
            a = ts[key + "_any"]           # в исходнике — и мягкие формы, иначе переформулировка сойдёт за новое
        na, nb = len(a), len(b)
        if direction == "more":
            slack = _b_slack(key, rb)
            lim = na + slack
            if nb <= lim:
                continue
            if key == "reveal" and len(tr["label_reveal"]) <= len(ts["label_reveal"]):
                continue            # ярлык стал раскрытием («Итог: …» → «Итог такой: …») — новых «:» нет
            src_set = {tk.fold_yo(h.text.strip()) for h in a}
            frs = [_fr("результат", h.text, h.match) for h in b if tk.fold_yo(h.text.strip()) not in src_set]
            out.append(Finding("B", "B", title, "hard", f"в исходнике {na}, в результате {nb}"
                               + (f" (допустимо {lim})" if slack else ""),
                               (frs or [_fr("результат", h.text, h.match) for h in b])[:MAX_FRAGS], hint))
        else:
            if na == 0:
                continue
            if key == "long":
                need = max(1, math.floor(BUDGETS["diff"]["long_keep"] * na + 0.5))
            elif key == "paren":
                need = max(1, math.floor(BUDGETS["diff"]["paren_keep"] * na + 0.5))
            else:
                need = na
            if nb >= need:
                continue
            res_set = {tk.fold_yo(h.text.strip()) for h in b}
            frs = [_fr("исходник", h.text, h.match) for h in a if tk.fold_yo(h.text.strip()) not in res_set]
            out.append(Finding("B", "B", title, "hard", f"в исходнике {na}, в результате {nb} (нужно не меньше {need})",
                               (frs or [_fr("исходник", h.text, h.match) for h in a])[:MAX_FRAGS], hint))
    # --- средняя фраза стала короче исходника (DEV-замер v2, P2): в rewrite — жёстко, в edit — мягко
    md = mean_drop(sh, rh)
    if md is not None:
        sm, rm, split = md
        frs = []
        for i, run in split[:2]:
            frs.append(_fr("исходник", sh.sents[i].raw, f"{sh.sents[i].n_words} слов"))
            frs.append(_fr("результат", " ".join(rh.sents[j].raw for j in run),
                           " + ".join(str(rh.sents[j].n_words) for j in run) + " слов"))
        if not frs:
            frs = [_fr("результат", s.raw, f"{s.n_words} слов")
                   for s in sorted((x for x in rh.sents if 0 < x.n_words <= 5), key=lambda x: x.n_words)[:MAX_FRAGS]]
        out.append(Finding("B", "B", "Средняя фраза стала короче исходника (больше чем на 10%)",
                           "hard" if mode == "rewrite" else "soft",
                           f"средняя фраза {rm:.1f} слова, в исходнике {sm:.1f} ({rm / sm - 1:+.0%})"
                           + (f"; поделено фраз: {len(split)}" if split else ""),
                           frs[:MAX_FRAGS],
                           "Не дробить: ярлык двоеточия снять, а не делать отдельной фразой; если фразу всё же "
                           "поделили по точке, рядом склеить другую пару через подчинение («который», «когда», "
                           "«если», «хотя», причастный оборот)."))
    # --- новое тире там, где было двоеточие или оборот (P5)
    turns = new_dash_turns(sb, rb)
    if turns:
        out.append(Finding("B", "B", "Новое тире на месте двоеточия или оборота", "hard",
                           f"{len(turns)}: " + "; ".join(h.match for h in turns[:4]),
                           [_fr("результат", h.text, h.match) for h in turns[:MAX_FRAGS]],
                           "Двоеточие не менять на тире: снять ярлык или поставить союз того отношения, что было; "
                           "оборот («заключается в создании», деепричастие) развернуть глаголом без тире "
                           "(«Я хочу создать капсулу»)."))
    return out


# =============================================================================== v4: провенанс (E), подача (F), лента (G)
# Владелец фразы (SKILL v4): А — автор (диктовка, сообщения, ответы, его текст в edit), И — источник фактов
# (бриф, новость), М — модель (всё остальное, в том числе черновик сверх фактов источника).
M_SHARE = 1 / 3          # фраза М: меньше трети содержательных слов из источника и материала (humanness 5.4)
BACKED_SHARE = 0.5       # фраза с опорой: не меньше половины содержательных слов из источника и материала
MIN_CONTENT = 2          # фразу из одного знаменательного слова («Подписывайтесь.») по долям не размечаем
ASSEMBLE_BIGRAMS_MIN = 0.5
TIMID_CHANGE = 0.05      # «робкая правка»: изменено меньше 5% слов черновика (PREREG раунда 2, 5.4 п. 3)


def detector_cfg(name: str) -> dict:
    """Точность детекторов E и F, замеренная на TEST (REVIEW.md v4): жёсткий флаг — только при точности ≥ 0,7."""
    return (BUDGETS.get("detectors") or {}).get(name, {})


def detector_sev(name: str, with_source: bool) -> str:
    cfg = detector_cfg(name)
    key = "hard_with_source" if with_source else "hard_no_source"
    return "hard" if cfg.get(key) else "soft"


@dataclass
class Prov:
    """Опорный текст для провенанса: источник фактов и материал автора (или, без них, исходник старого вызова)."""
    ref: tk.Doc | None                 # источник ∪ материал; в старом вызове — сам исходник (черновик или текст автора)
    material: tk.Doc | None
    distinct: bool                     # опора отличается от черновика правки (есть --draft и источник/материал, или write)
    authored: bool                     # опора — слова автора (edit, диктовка, материал): её концовки и рамки — А
    keys: set = field(default_factory=set)
    mat_keys: set = field(default_factory=set)
    nums: dict = field(default_factory=dict)
    cleaned: list = field(default_factory=list)   # снятое М: (что, фраза черновика)
    m_cut: bool = False                # из черновика вырезана хотя бы одна фраза М (нижняя граница длины 70%)
    no_source: bool = False            # v5: rewrite без источника — опора только черновик, концовки с содержанием «А?»
    v5: dict = field(default_factory=dict)   # v5: метки черновика, снятая рамка, слова рамки для предела сокращения
    ref_flat: str = ""                 # опора строчными без пробелов: латиница слитно и раздельно («StackOverflow»)

    @classmethod
    def build(cls, ref_text: str | None, material_text: str | None, distinct: bool, authored: bool) -> "Prov":
        parts = [t for t in (ref_text, material_text) if t]
        ref = tk.Doc("\n\n".join(parts)) if parts else None
        mat = tk.Doc(material_text) if material_text else None
        p = cls(ref, mat, distinct, authored)
        if ref is not None:
            p.keys = tk.all_keys(ref)
            p.nums = numbers_in(ref)
            p.ref_flat = re.sub(r"\s+", "", tk.fold_yo(ref.text.lower()))
        if mat is not None:
            p.mat_keys = tk.all_keys(mat)
        return p

    def share(self, s: tk.Sent, keys: set | None = None) -> float | None:
        return sent_share(s, self.keys if keys is None else keys)

    def num_backed(self, v: str, rec: dict) -> bool:
        return _num_count(v, rec, self.nums) > 0

    def name_backed(self, var: set) -> bool:
        return bool(var & self.keys)

    def sent_backed(self, s: tk.Sent) -> bool:
        sh = self.share(s)
        return sh is None or sh >= BACKED_SHARE


def sent_share(s: tk.Sent, keys: set) -> float | None:
    """Доля знаменательных слов фразы, найденных в опоре (лемма или основа). None — меньше MIN_CONTENT слов."""
    toks = [t for t in s.words if tk.is_content(t)]
    if len(toks) < MIN_CONTENT:
        return None
    return sum(1 for t in toks if tk.tok_variants(t) & keys) / len(toks)


def content_bigrams(doc: tk.Doc) -> list[tuple[str, str]]:
    out = []
    for s in doc.sents:
        ks = [tk.word_key(t) for t in s.words if tk.is_content(t)]
        out += list(zip(ks, ks[1:]))
    return out


_WORD_RX = re.compile(r"\w+", re.U)


def changed_words(a: str, b: str) -> int:
    """Изменённых слов, как в bench/test/metrics/report_extra.py и bench/round2/e0/common.py."""
    ta, tb = _WORD_RX.findall(a.lower()), _WORD_RX.findall(b.lower())
    return sum(max(a2 - a1, b2 - b1)
               for op, a1, a2, b1, b2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes()
               if op != "equal")


def change_share(a: str, b: str) -> float:
    n = len(_WORD_RX.findall(a))
    return changed_words(a, b) / n if n else 0.0


def _sent_has_number(doc: tk.Doc, i: int, nums: dict | None = None) -> bool:
    nums = numbers_in(doc) if nums is None else nums
    return any(i in r["sents"] and r["report"] for r in nums.values())


def _sent_names(doc: tk.Doc, names: list | None = None) -> set[int]:
    names = name_candidates(doc) if names is None else names
    return {i for _, _, i in names}


def content_sent_ids(doc: tk.Doc) -> list[int]:
    """Фразы со словами, кроме строк из одних хэштегов, ссылок и эмодзи (они замаскированы в Doc)."""
    return [i for i, s in enumerate(doc.sents) if s.words]


# --------------------------------------------------------------- F1: концовка
END_GENERAL_RX = (r"\b(?:все|всем|всех|каждый|каждого|каждому|каждая|каждой|каждое|всегда|никогда|главное|"
                  r"стоит|стоило|нужно|важно|любой|любая|любое|любому)\b(?!-)")     # «всё-таки» — не обобщение
END_CALL_RX = (r"\b(?:подписывайтесь|подпишитесь|пишите|напишите|делитесь|поделитесь|переходите|перейдите|читайте|"
               r"прочитайте|смотрите|посмотрите|присоединяйтесь|приходите|заходите|оставляйте|оставьте|ставьте|"
               r"расскажите|попробуйте|пробуйте|не забудьте|не забывайте|не пропустите|не упустите|регистрируйтесь|"
               r"записывайтесь|посетите|давайте|помните|не бойтесь|берегите|узнайте|спешите|успейте|жду вас|ждем вас|"
               r"ждём вас)\b")
END_THANKS_RX = r"\b(?:спасибо|благодарю|благодарим|благодарны|благодарен|благодарна|благодарность)\b"
END_WISH_RX = (r"\b(?:желаю|желаем|пусть|удачи|успехов|хорошего (?:дня|вечера|настроения)|хороших выходных|"
               r"до встречи|до новых встреч|надеюсь|надеемся|будем рады|буду рад|буду рада)\b")
END_SUMMARY_RX = (r"^\W*(?:таким образом|в итоге|итак|в заключение|подводя итог\w*|в общем|итог|вывод|как видите|"
                  r"как видим|получается|в конечном счете|в конце концов|одним словом)\b")
END_KINDS = (("итог", END_SUMMARY_RX), ("благодарность", END_THANKS_RX), ("пожелание", END_WISH_RX),
             ("призыв", END_CALL_RX), ("обобщение", END_GENERAL_RX))
ENDING_SENTS = 2          # последние 1–2 фразы (план v4, 3.4)


def _is_question(s: tk.Sent) -> bool:
    return bool(re.search(r"\?[^\w]*$", s.norm.strip()))


def _ends_with(raw: str, ch: str) -> bool:
    t = tk.EMOJI_RX.sub("", raw.strip())
    t = re.sub(r"[\s*_#)\]]+$", "", t)
    return t.endswith(ch)


def _impr_call(s: tk.Sent) -> bool:
    """Повелительное 2-го лица мн. ч. («Пробуйте», «Посетите») — призыв к читателю."""
    for t in s.words:
        w = t.w
        if w is not None and "impr" in w.tags and "plur" in w.tags and "excl" not in w.tags:
            return True
    return False


# v5, профиль gigachat (раунд 2, Э6, api/RESULT_API.md §3.4): F1 в широком виде срабатывал у 17 текстов GigaChat и
# 19 людей из 60 и пропустил оба вывода «Теперь…» реального автопостера. Для gigachat F1 сужен до формул:
# итог-формула, благодарность за внимание, пожелание-формула, призыв подписаться или написать в комментариях,
# и «Теперь …» в последней фразе. Обобщение («главное», «всегда», «нужно») и вопрос читателю не флажатся.
GIGA_SUMMARY_RX = r"^\W*(?:таким образом|в заключение|подводя итог\w*|в итоге|итак|как видите|как видим)\b"
GIGA_THANKS_RX = (r"\b(?:спасибо|благодарю|благодарим)\s+(?:вам\s+|всем\s+)?(?:за внимание|за прочтение|что дочитали|"
                  r"что читаете|что (?:вы )?с нами|за то,? что (?:дочитали|читаете))")
GIGA_WISH_RX = (r"\b(?:удачи|успехов|хорошего (?:дня|вечера|настроения)|хороших выходных|до встречи|до новых встреч|"
                r"будем рады|буду рад|буду рада)\b")
GIGA_CALL_RX = (r"\b(?:подписывайтесь|подпишитесь|ставьте лайк\w*|делитесь (?:постом|с друзьями)|"
                r"(?:пишите|напишите|делитесь|оставляйте|расскажите)(?:\s+\w+){0,3}?\s+в\s+комментари\w*|"
                r"оставляйте комментари\w*)")
THEN_LAST_RX = r"^\W*(?:а\s+|и\s+)?теперь\b(?!\s+(?:про|о|об|к)\s)(?!\s+(?:сам\s+|самый\s+)?вопрос)"


def ending_kinds(s: tk.Sent, profile: str | None = None, last: bool = False) -> list[str]:
    txt = s.norm.strip()
    if profile == "gigachat":
        out = [k for k, p in (("итог", GIGA_SUMMARY_RX), ("благодарность", GIGA_THANKS_RX),
                              ("пожелание", GIGA_WISH_RX), ("призыв", GIGA_CALL_RX)) if rx(p).search(txt)]
        if last and rx(THEN_LAST_RX).search(txt) and not _is_question(s):
            out.append("вывод «Теперь…»")
        return out
    out = [k for k, p in END_KINDS if rx(p).search(txt)]
    if "призыв" not in out and _impr_call(s):
        out.append("призыв")
    if _is_question(s):
        out.append("вопрос читателю")
    return out


def ending_candidates(doc: tk.Doc, k: int = ENDING_SENTS) -> list[int]:
    ids = content_sent_ids(doc)
    return ids[-k:] if ids else []


def ending_hits(doc: tk.Doc, prov: Prov | None = None, use_ref: bool = False, k: int = ENDING_SENTS,
                profile: str | None = None) -> list[tuple[int, list[str]]]:
    """F1: фразы среди последних k со словами обобщения, призывом, благодарностью, пожеланием, итогом или
    вопросом читателю — без чисел и имён. С опорой (use_ref) фраза, у которой не меньше половины слов есть
    в источнике или материале, — концовка А или И, не флажится."""
    nums = numbers_in(doc)
    named = _sent_names(doc)
    out = []
    cands = ending_candidates(doc, k)
    for i in cands:
        s = doc.sents[i]
        kinds = ending_kinds(s, profile, last=bool(cands) and i == cands[-1])
        if not kinds or (_sent_has_number(doc, i, nums) or i in named) and profile != "gigachat":
            continue
        if use_ref and prov is not None and prov.ref is not None:
            sh = prov.share(s)
            if sh is not None and sh >= BACKED_SHARE:
                continue
            if sh is None and _phrase_in_ref(s, prov):
                continue
        out.append((i, kinds))
    return out


def _phrase_in_ref(s: tk.Sent, prov: Prov) -> bool:
    """Короткая фраза («Подписывайтесь.», «Спасибо!») есть в опоре почти дословно."""
    ws = [t for t in s.words]
    return bool(ws) and all(tk.tok_variants(t) & prov.keys for t in ws)


# --------------------------------------------------------------- F2: связки-анонсы (списки — phrase_screen.out раунда 2)
ANNOUNCE_RX = (
    r"^\W*(?:но\s+)?важнее другое\b"
    r"|^\W*(?:а\s+|и\s+)?теперь\s+(?:про|о|об|к)\s"
    r"|\bдальше\s*[—–-]?\s*(?:интереснее|больше|веселее|хуже|лучше|сложнее)\b"
    r"|^\W*(?:суть|идея|мысль|логика|схема|принцип|причина|ответ|правило|механика)\s+(?:простая|проста|простой|такая|"
    r"такова|очевидна|очевидная)\s*[.!]"
    r"|^\W*вот что\s+(?:в списке|важно|нужно знать|получилось|вышло|я понял|мы узнали)\b"
    r"|^\W*да,\s+(?:название|звучит|слово)\b"
    r"|^\W*(?:и\s+)?что (?:это|все это) (?:значит|означает|дает)\b"
    r"|^\W*почему это (?:важно|работает)\??"
    r"|^\W*как это работает\??\s*$"
    r"|^\W*иными словами\b"
    r"|\bдавайте разберемся\b"
    r"|^\W*и вот (?:тут|здесь)\b"
)

# --------------------------------------------------------------- F3: лишнее пояснение
EXPLAIN_RX = r"\b(?:то есть|иными словами|другими словами|иначе говоря|а значит|проще говоря|по сути)\b"
EXPLAIN_SHARE = 0.7


def _keys_of(toks) -> set:
    return {v for t in toks if tk.is_content(t) for v in tk.tok_variants(t)}


def explain_hits(doc: tk.Doc) -> list[tuple[int, str]]:
    """Фраза с «то есть / иными словами / а значит», у которой не меньше 70% знаменательных слов уже есть
    в предыдущей фразе (или, если маркер внутри фразы, в её части до маркера)."""
    out = []
    r = rx(EXPLAIN_RX)
    for i, s in enumerate(doc.sents):
        m = r.search(s.norm)
        if not m:
            continue
        before = s.norm[:m.start()]
        after_toks = [tk.make_tok(x) for x in tk.tokenize(s.norm[m.end():])]
        after = [t for t in after_toks if tk.is_content(t)]
        if len(after) < 2:
            continue
        if len(_WORD_RX.findall(before)) <= 2:            # маркер в начале: сравнить с предыдущей фразой
            if i == 0:
                continue
            prev = _keys_of(doc.sents[i - 1].words)
        else:
            prev = _keys_of(tk.make_tok(x) for x in tk.tokenize(before))
        share = sum(1 for t in after if tk.tok_variants(t) & prev) / len(after)
        if share >= EXPLAIN_SHARE:
            out.append((i, m.group(0)))
    return out


# --------------------------------------------------------------- F4: рамка промо
TEASER_RX = (r"\b(?:вы узнаете|узнаете|из (?:статьи|поста|видео|материала|ролика) вы узнаете|"
             r"в (?:статье|посте|видео|материале|ролике|выпуске) (?:расскажем|рассказываем|разберем|разбираем|узнаете)|"
             r"(?:он|она|они|мы|я) расскаж\w+|расскажем|сегодня рассказываем|читайте в (?:статье|нашем|новом))\b")
PROMO_CALL_RX = (r"\b(?:переходите|перейдите|читайте|смотрите|подписывайтесь|подпишитесь|присоединяйтесь|"
                 r"регистрируйтесь|записывайтесь|приходите|посетите|делитесь|поделитесь|пишите|пробуйте|"
                 r"попробуйте|узнайте|не пропустите|не упустите|успейте|спешите|заходите|ставьте|оставляйте|"
                 r"жду вас|ждем вас|ждём вас)\b")


def promo_parts(doc: tk.Doc) -> dict[str, str]:
    """Части рамки промо-поста: вопрос-приманка и восклицание в зачине (первая фраза или строка-заголовок),
    тизер «Вы узнаете / расскажем», список, призыв из списка глаголов. Значение — фраза, где нашлась часть."""
    parts: dict[str, str] = {}
    ids = content_sent_ids(doc)
    if ids:
        first = doc.sents[ids[0]]
        if _ends_with(first.raw, "?"):
            parts["вопрос в зачине"] = first.raw
        elif _ends_with(first.raw, "!"):
            parts["восклицание в зачине"] = first.raw
    for i in ids:
        s = doc.sents[i]
        if "тизер «вы узнаете»" not in parts and rx(TEASER_RX).search(s.norm):
            parts["тизер «вы узнаете»"] = s.raw
        # повелительное в пункте списка — шаг инструкции («Шаг 2: Перейдите в раздел…»), а не призыв
        if "призыв" not in parts and rx(PROMO_CALL_RX).search(s.norm) and not _on_list_line(doc, s):
            parts["призыв"] = s.raw
    lists = block_lists(doc)
    if lists:
        parts["список"] = lists[0][0]
    return parts


PROMO_MIN_PARTS = 2


def _on_list_line(doc: tk.Doc, s: tk.Sent) -> bool:
    """Фраза в пункте списка: строка «- …», «1. …» или эмодзи-маркер, если соседняя строка тоже с эмодзи."""
    def emo(k):
        return 0 <= k < len(doc.mlines) and bool(doc.mlines[k].strip()) and bool(
            tk.EMOJI_RX.match(doc.mlines[k].strip()[:1]))
    k = s.line
    raw = doc.mlines[k] if k < len(doc.mlines) else ""
    return bool(LIST_LINE_RX.match(raw)) or (emo(k) and (emo(k - 1) or emo(k + 1)))

# --------------------------------------------------------------- F5: заглушки
PLACEHOLDER_RX = re.compile(
    r"\[(?:уточнить|ссылк|имя|имен|название|дата|дату|фото|вставить|ваш|номер|контакт|место|город|время|цена|"
    r"цену|адрес|телефон|ник|link|url|tbd|todo|здесь|сюда|подставить|укажите|указать|x+\]|х+\])[^\]\n]{0,80}\]"
    r"|\]\((?:ссылка|link|url|#)[^)\n]{0,40}\)"
    r"|\[(?:по|на|в|см\.?)\s+(?:ссылк|линк|link|url)[^\]\n]{0,40}\](?!\()"      # «[по ссылке]» (v5, opinion-138)
    r"|\((?:ссылка|link)-на-[^)\n]{0,40}\)"
    r"|(?<![\w])(?:XXX+|ХХХ+)(?![\w])"
    r"|[<{](?:имя|название|ссылка|дата|город|link|name)[>}]",
    re.I)


def placeholder_hits(doc: tk.Doc) -> list[Hit]:
    out = []
    for raw, _ in doc.lines:
        out += [Hit(raw, m.group(0)) for m in PLACEHOLDER_RX.finditer(raw)]
    return out


# --------------------------------------------------------------- F6: подзаголовки и рубрики
_MD_HEAD_RX = re.compile(r"^\s*#{1,6}\s+\S")
_BOLD_LINE_RX = re.compile(r"^\s*(?:[^\w\s*]{1,4}\s*)?\*\*[^*\n]{2,90}\*\*\s*[:.!?]?\s*(?:[^\w\s*]{1,4})?\s*$")
_TERMINAL = ".!?…;,:»\")"


def heading_lines(text: str) -> list[tuple[int, str]]:
    """Строки-заголовки: markdown «#», строка целиком жирным, короткая строка без конечного знака (до 8 слов),
    за которой идёт текст. Пункты списков, ссылки, хэштеги и подпись в конце не считаются."""
    lines = [l for l in (text or "").replace("\r\n", "\n").split("\n")]
    nonblank = [(k, l) for k, l in enumerate(lines) if l.strip()]
    out = []
    for n, (k, l) in enumerate(nonblank):
        st = l.strip()
        if _MD_HEAD_RX.match(st) or _BOLD_LINE_RX.match(st):
            out.append((k, st))
            continue
        if n == len(nonblank) - 1 or LIST_LINE_RX.match(st) or tk.URL_RX.search(st) or st.startswith("#"):
            continue
        plain = tk.EMOJI_RX.sub("", st).strip()
        words = _WORD_RX.findall(plain)
        if not (1 <= len(words) <= 8) or plain[-1:] in _TERMINAL or not plain[:1].isupper():
            continue
        # за строкой — абзац (пустая строка или длинная строка текста), а не продолжение стихов/перечня
        nxt = nonblank[n + 1][1].strip()
        gap = nonblank[n + 1][0] - k
        if len(_WORD_RX.findall(nxt)) >= 6 or gap >= 2:
            out.append((k, st))
    return out


# --------------------------------------------------------------- F7: шаблоны gigachat и yandex (phrase_screen.out)
TEMPLATE_RX = (
    r"\bвдохновля\w* пример\w*|\bнов\w+ (?:высот|вершин)\w*|\bбоят\w+ трудност\w+|\bдвига\w+ вперед\b"
    r"|\bдвинуться вперед\b|\bвол\w+ в кулак\b|\bвер\w+ в себя\b|\bярк\w+ пример\w*|\bнастоящ\w+ профессионал\w*"
    r"|\bбудем рады\b|\bне упусти\w* (?:шанс|возможност)\w*|\bуникальн\w+ возможност\w*"
    r"|\bнезабываем\w+ (?:впечатлен|эмоци|момент)\w*|\bморе (?:позитива|эмоций|удовольствия)\b"
    r"|\bзалог\w* успеха\b|\bключ\w* к успеху\b|\bистори\w+ успеха\b|\bогромн\w+ потенциал\w*"
    r"|\bвн(?:ес|осит|осят|ести|осить)\w* (?:свой |огромный |значительный |весомый )?вклад\b|\bприятно удив\w+"
    r"|\bдоби\w+ успеха\b|\bмир\w* возможност\w+|\bзаряд\w* (?:энерги|позитив|бодрост)\w*"
)
TEMPLATE_PROFILES = ("gigachat", "yandex", "core")

# --------------------------------------------------------------- E: оценочные слова (humanness 5.4, GIGA-07)
EVAL_RX = (r"\b(?:потрясающ|вдохновля|вдохновен|знаков|инновацион|успешн|ключев|уникальн|невероятн|удивительн|"
           r"великолепн|грандиозн|впечатляющ|выдающ|революцион|незабываем|увлекательн|восхитительн|блестящ|"
           r"замечательн|прекрасн|потрясн|колоссальн|феноменальн|эффективн|важнейш|стратегическ|амбициозн)\w*")


def eval_words(doc: tk.Doc) -> list[tuple[int, tk.Tok]]:
    r = rx(EVAL_RX + r"$")
    out = []
    for i, s in enumerate(doc.sents):
        for t in s.words:
            if r.match(t.low):
                out.append((i, t))
    return out


def _derived_small(v: str, doc: tk.Doc) -> bool:
    """«два подразделения», «три офиса», «оба» — счёт перечисленного, а не новый факт: числа до 3, записанные
    словом, E2 не считает (цифрой — считает)."""
    try:
        x = float(v)
    except ValueError:
        return False
    return x <= 3 and not re.search(rf"(?<![\d.,]){re.escape(v)}(?![\d])", doc.norm)


def fact_names(doc: tk.Doc) -> list[tuple[set, str, int]]:
    """Имена для E2: словарные имена, фамилии, топонимы и организации, незнакомые слова с заглавной не в начале
    фразы и латиница с заглавной от 4 букв. Термины-аббревиатуры (HR, IT, AI, UX) и латиница со строчной — не имена."""
    out = []
    for var, text, i in name_candidates(doc):
        t = tk.make_tok(text)
        if t.is_latin:
            if len(text) >= 4 and text[:1].isupper() and not (text.isupper() and len(text) <= 4):
                out.append((var, text, i))
        elif re.match(r"^[A-Z]{1,4}-", text):
            continue                              # «IT-компании», «HR-отдел» — термин, не имя
        elif t.w is not None and not t.w.known and len(text) > 3:
            # незнакомое слово с заглавной (в том числе «имя» по догадке морфологии) — имя, только если оно не первое
            # во фразе («Постебался.», «Задолбали, …», «Фаундеры упустили…») и не крик капсом («ПААМААГИИТЕЕ!!!»);
            # разбор E2 на TEST, REVIEW.md v4
            if _first_word(doc.sents[i]) == text or (text.isupper() and len(text) > 5):
                continue
            out.append((var, text, i))
        elif tk.is_proper(t.w):
            out.append((var, text, i))
        elif text.isupper() and len(text) >= 2 and not tk.has_morph():
            out.append((var, text, i))
    return out


def _first_word(s: tk.Sent) -> str | None:
    """Первое слово фразы после нумерации пункта («3.», «2)»)."""
    for t in s.words:
        if t.is_num and len(t.text) <= 2:
            continue
        return t.text
    return None


def _name_in_ref(var: set, text: str, prov: Prov) -> bool:
    if var & prov.keys:
        return True
    low = tk.fold_yo(text.lower())
    stem = low[:max(4, len(low) - 2)]            # «interviews» ~ «interview», «Хабре» ~ «Хабр»
    if any(k.startswith(stem) or low.startswith(k) and len(k) >= 4 for k in prov.keys):
        return True
    # латиница внутри слитного написания источника: «Stack Overflow» ~ «StackOverflow», «Overflow» ~ «stackoverflow»
    return tk.make_tok(text).is_latin and len(low) >= 4 and low in prov.ref_flat


def _next_to_backed_name(doc: tk.Doc, j: int, text: str, prov: Prov) -> bool:
    """Часть имени при имени из источника: «Энтони Хопкинсом», когда в источнике «Хопкинс»."""
    ws = doc.sents[j].words
    for k, t in enumerate(ws):
        if t.text != text:
            continue
        for n in (k - 1, k + 1):
            if not (0 <= n < len(ws)):
                continue
            nb = ws[n]
            name_like = nb.text[:1].isupper() and len(nb.text) >= 3 and (
                tk.is_proper(nb.w) or nb.is_latin or (nb.w is not None and not nb.w.known))
            if name_like and _name_in_ref(tk.tok_variants(nb), nb.text, prov):
                return True
    return False


def _eval_in_ref(t: tk.Tok, prov: Prov) -> bool:
    if tk.tok_variants(t) & prov.keys:
        return True
    st = t.low[:6]
    return any(k.startswith(st) for k in prov.keys) if len(st) >= 6 else False


# --------------------------------------------------------------- «фраза от лица автора»
def authorial(s: tk.Sent) -> bool:
    """Фраза говорит голосом автора: «я / мне / мой», глагол 1-го лица ед. ч., рамка мнения."""
    t = s.norm
    if rx(FP_RX).search(t) or rx(OPINION_STRICT).search(t):
        return True
    for tok in s.words:
        w = tok.w
        if w is not None and w.pos == "VERB" and "1per" in w.tags and "sing" in w.tags:
            return True
    return False


# --------------------------------------------------------------- блок E
def block_e(res: tk.Doc, base: tk.Doc | None, prov: Prov, mode: str, assemble: bool, base_text: str | None,
            res_text: str) -> tuple[list[Finding], dict]:
    out: list[Finding] = []
    info: dict = {"m_sentences": [], "last_m": False, "shares": [], "change_share": None}
    if prov.ref is None:
        return out, info
    ref_name = "источника и материала" if prov.distinct else "исходника"
    # --- доли по фразам и список фраз М
    m_ids = []
    for i, s in enumerate(res.sents):
        sh = prov.share(s)
        info["shares"].append(None if sh is None else round(sh, 2))
        if sh is not None and sh < M_SHARE:
            m_ids.append(i)
    info["m_sentences"] = [res.sents[i].raw.strip() for i in m_ids]
    # --- E1: последняя фраза — М
    cand = [i for i in content_sent_ids(res)[-2:] if prov.share(res.sents[i]) is not None]
    if cand:
        last = cand[-1]
        sh = prov.share(res.sents[last])
        if sh < M_SHARE:
            info["last_m"] = True
            sev = detector_sev("E1_last_m", prov.distinct or prov.authored)
            out.append(Finding("E", "E1", "Последняя фраза — М", sev,
                               f"в ней {sh:.0%} знаменательных слов из {ref_name} (М — меньше трети)",
                               [_fr("результат", res.sents[last].raw)],
                               "Последняя фраза не может быть М: кончить последним фактом источника или мыслью автора; "
                               "снятую фразу перечислить в заметке («убрал, верни, если это твоё»)."))
    if m_ids:
        out.append(Finding("E", "E0", "Фразы М (меньше трети слов из опоры)", "note",
                           f"{len(m_ids)} из {len(res.sents)}", [_fr("результат", res.sents[i].raw)
                                                                 for i in m_ids[:MAX_FRAGS]],
                           "М допустима только как связка: оценку, мораль, призыв, эпизод не из источника снять.",
                           counted=False))
    # --- E2: числа и имена, которых нет в источнике и материале, но есть в черновике (М-факты черновика)
    if prov.distinct and base is not None:
        rn = numbers_in(res)
        bn = numbers_in(base)
        kept = [v for v, r in rn.items() if r["report"] and not prov.num_backed(v, r) and _num_count(v, r, bn) > 0
                and not _derived_small(v, res) and v != "1"]       # «1 раз», «1 пост — 1 мысль»: как слово «один»
        if kept:
            out.append(Finding("E", "E2", "Числа не из источника", detector_sev("E2_numbers", True),
                               "есть в черновике, нет в источнике и материале: "
                               + ", ".join(f"«{_num_show(v)}»" for v in kept),
                               [_fr("результат", res.sents[rn[v]["sents"][0]].raw) for v in kept][:MAX_FRAGS],
                               "Число, которого нет в источнике, придумала модель: убрать или проверить по источнику."))
        b_all = tk.all_keys(base)
        names, seen = [], set()
        for var, text, j in fact_names(res):
            if (_name_in_ref(var, text, prov) or not (var & b_all) or text.lower() in seen
                    or _next_to_backed_name(res, j, text, prov)):
                continue
            seen.add(text.lower())
            names.append((text, j))
        if names:
            out.append(Finding("E", "E2", "Имена и названия не из источника", detector_sev("E2_names", True),
                               ", ".join(f"«{t}»" for t, _ in names[:10]),
                               [_fr("результат", res.sents[j].raw, ", ".join(t for t, jj in names if jj == j))
                                for j in dict.fromkeys(j for _, j in names)][:MAX_FRAGS],
                               "Имя или название, которого нет в источнике и материале, придумала модель: убрать."))
    # --- E3: оценочные слова не из опоры
    ev = [(i, t) for i, t in eval_words(res) if not _eval_in_ref(t, prov)]
    if ev:
        sev = detector_sev("E3_eval", prov.distinct or prov.authored)
        out.append(Finding("E", "E3", "Оценочные слова не из источника", sev,
                           ", ".join(dict.fromkeys(f"«{t.text}»" for _, t in ev)),
                           [_fr("результат", res.sents[i].raw, t.text) for i, t in ev][:MAX_FRAGS],
                           "Оценку, которой нет у автора и в источнике, снять; оценка из источника остаётся."))
    # --- E4: фраза от лица автора без опоры в материале (5.6 п. 2)
    if prov.material is not None:
        bad = []
        for i, s in enumerate(res.sents):
            if not authorial(s):
                continue
            sh = prov.share(s)
            if sh is not None and sh < BACKED_SHARE:
                bad.append((i, sh))
        if bad:
            out.append(Finding("E", "E4", "Фраза А без опоры в материале", "hard",
                               f"{len(bad)} фраз от лица автора, у которых меньше половины слов из материала и источника",
                               [_fr("результат", res.sents[i].raw, f"{sh:.0%}") for i, sh in bad][:MAX_FRAGS],
                               "Голос автора — только из его сообщений: фразу снять или вернуть его словами."))
    # --- E5: сборка (v5) — каждая строка заметок есть в тексте (жёстко); доля биграмм и фразы М — справка
    if assemble:
        mat_text = prov.material.text if prov.material is not None else prov.ref.text
        unc = coverage_lines(mat_text, res_text)
        info["uncovered"] = [l for l, _ in unc]
        if unc:
            out.append(Finding("E", "E5", "Сборка: строка заметок не найдена в тексте", "hard",
                               f"{len(unc)}: в тексте меньше половины слов строки",
                               [_fr("заметки", l, f"{sh:.0%}") for l, sh in unc][:MAX_FRAGS],
                               "Каждая строка заметок — в тексте, словами автора и в его порядке. Если строка — "
                               "поручение или пометка о форме («дам ссылку», «теги…», «с иронией»), выполнить её "
                               "и написать об этом в заметке; ссылку-заглушку не ставить."))
        rb = content_bigrams(res)
        refb = set(content_bigrams(prov.ref))
        share = sum(1 for b in rb if b in refb) / len(rb) if rb else 1.0
        info["assemble_bigrams"] = round(share, 2)
        if rb and share < ASSEMBLE_BIGRAMS_MIN:
            out.append(Finding("E", "E5", "Сборка: мало слов автора", "note",
                               f"содержательных биграмм из материала {share:.0%} — справка, не правило v5",
                               hint="Брать фрагменты автора с минимальной правкой, синонимы «для красоты» не ставить.",
                               counted=False))
        lim = max(1, res.n_words // 100)
        if len(m_ids) > lim:
            out.append(Finding("E", "E5", "Сборка: фраз М больше одной на 100 слов", "note",
                               f"{len(m_ids)} — справка: проверь, что это только связки",
                               [_fr("результат", res.sents[i].raw) for i in m_ids][:MAX_FRAGS],
                               "В сборке М — только связки; пункты сверх материала не добавлять.", counted=False))
    # --- снятое М (из блока A)
    if prov.cleaned:
        out.append(Finding("E", "E7", "Снято М (чистка, не потеря)", "note",
                           "; ".join(trim(w, 60) for w, _ in prov.cleaned[:8])
                           + " — этого нет в источнике и материале; перечислить в заметке автору",
                           [_fr("черновик", t) for _, t in prov.cleaned if t][:MAX_FRAGS], counted=False))
    if base_text is not None and mode != "write":
        info["change_share"] = round(change_share(base_text, res_text), 3)
    return out, info


def timid_finding(info: dict, findings: list[Finding]) -> list[Finding]:
    """E6 «робкая правка»: изменено меньше 5% слов черновика, а E или F нашли, что править."""
    cs = info.get("change_share")
    if cs is None or cs >= TIMID_CHANGE:
        return []
    found = [f for f in findings if f.block in "EF" and f.severity in ("hard", "soft")]
    if not found:
        return []
    return [Finding("E", "E6", "Робкая правка", "soft",
                    f"изменено {cs:.1%} слов черновика при {len(found)} находках E и F "
                    f"({', '.join(dict.fromkeys(f.code for f in found))})",
                    hint="Правило без правки не работает: снять М, концовку, рамку промо и шаблоны, а не только "
                         "счётчики. Меньше 5% изменённых слов в раунде 2 — вердикт «правила не срабатывают».")]


# =============================================================================== v5: концовка автора, следы площадки
# Раунд 2 (bench/round2/RESULT.md §7.2, §13): без источника v4 снимал последнюю фразу как мораль модели и в 11 случаях
# из 20 потерь срезал вывод, совет, пожелание, призыв или вопрос автора, ещё в 5 — хэштеги, ссылки и подпись.
# v5: без источника фраза черновика с действием или утверждением, в которой есть содержательные леммы, которых нет
# в остальном тексте, — «А?» (может быть словами автора): её можно упростить, но не удалять. Удалять можно только
# рамку модели: пустые формулы, повторы, обёртку и хвосты ответа, строку-заголовок. Вопрос читателю не трогать.
# Следы площадки (хэштеги, @-подписи, ссылки, «заранее спасибо», «всем добра») — часть текста автора.
V5_SHORTEN_MAX = 0.10      # без источника сократить можно не больше чем на 10% слов, и только за счёт рамки модели
FINAL_SENTS = 2            # зона концовки: последние две фразы с содержанием и весь их абзац
COVER_SHARE = 0.5          # сборка: строка заметок найдена, если в тексте не меньше половины её знаменательных слов

# пустые формулы: благодарность, «будем рады», подписка — до конца клаузы; остальное — только сами слова формулы
FORMULA_CLAUSE_RX = (
    r"(?<!заранее )\b(?:спасибо|благодарю|благодарим|благодарны|благодарен|благодарна)\b[^.!?]*"
    r"|\b(?:будем рады|буду рад|буду рада|рады (?:видеть|приветствовать))\b[^.!?]*"
    r"|\b(?:подписывайтесь|подпишитесь|не забудьте подписаться|ставьте лайк\w*|лайкайте|репостите|"
    r"сохраняйте (?:пост|себе))\b[^.!?]*"
    r"|\b(?:желаю|желаем)\s+(?:всем\s+|вам\s+)?(?:удачи|успехов|хорошего|отличного|приятного|здоровья)\b[^.!?]*"
    r"|\b(?:всем\s+)?(?:удачи|успехов|хорошего (?:дня|вечера|настроения)|хороших выходных|"
    r"до (?:новых |скорых )?встреч\w*)\b")
FORMULA_WORDS_RX = (
    r"\b(?:пишите|напишите|оставляйте|оставьте|расскажите|делитесь|поделитесь)(?:\s+\w+){0,3}?\s+в\s+комментари\w*"
    r"|^\W*(?:таким образом|в заключение|подводя итог\w*|в итоге|итак|как видите|как видим|в общем|одним словом|"
    r"так что|вывод(?:\s+(?:простой|такой|прост|один))?)\b\s*[,:—–-]?")
# слова, которые после снятия формулы содержанием не считаются («Делитесь мнением в комментариях!»)
FORMULA_GENERIC = frozenset("мнение мысль впечатление отзыв вопрос комментарий идея друг лайк подписка обновление "
                            "терпение здоровье сила вдохновение успех настроение".split())
# рамка модели: ярлык в начале, крючок, анонсы, обращения, «честно», «дело в том, что», «главное —»
FRAME_V5_RX = (
    r"^\W*(?:[^\W\d_]+(?:\s+[^\W\d_]+){0,2})\s*:(?=\s|$)"
    r"|^\W*(?:хотите|хотели бы|знаете ли вы|задумывались ли вы|задумывались|мечтаете|устали)"
    r"(?:\s+(?:узнать|понять|разобраться|научиться|получить))?\b"
    r"|\bвы узнаете\b|\bдело в том,? что\b|\bглавное\s*[—–-]|\bсамое главное\b"
    r"|^\W*(?:а\s+|и\s+)?(?:теперь|вот|и вот)\s+(?:\w+\s+)?(?:новост\w*|главн\w*|интересн\w*|сюрприз\w*)\b[^.!?]*"
    r"|^\W*(?:а\s+|и\s+)?теперь\b"
    r"|^\W*вот\s+(?:такой|такая|такие|так|как это (?:сделать|работает)|что получилось)\b[^.!?]*"
    r"|^\W*(?:расскажу|расскажем|покажу|объясню),?\s+(?:как|что|почему)\b[^.!?]*")
WRAPPER_RX = (r"^\W*(?:конечно[!,.]|вот (?:пост|текст|вариант|отредактированн\w+|переписанн\w+|готов\w+)\b|"
              r"если хотите,? (?:я )?могу|что (?:поправил|изменил|сделал)\s*:|надеюсь,? (?:это|текст|пост) "
              r"(?:поможет|подойдет))")
HOOK_RX = (r"^\W*(?:хотите|хотели бы|знаете ли|знаете,? |задумывались|мечтаете|ищете|устали|интересно,? |"
           r"а вы знали)")
SEPARATOR_RX = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,}|—{2,}|={3,})\s*$")
TRACE_PHRASE_RX = (r"заранее спасибо|заранее благодар\w*|всем добра|добра всем|всем мира|мира всем|"
                   r"(?:коммент\w*|пост\w*)\s+для\s+минусов|минусы\s+сюда|для\s+минусов|"
                   r"^\W*источник\s*:|^\W*фото\s*:|^\W*автор\s*:|^\W*via\b")
CONTACT_CLASSES = (("ссылка", r"\b(?:ссылк\w*|линк\w*)"),
                   ("ник", r"\bник(?:а|у|ом|е|нейм\w*)?\b"),
                   ("контакты", r"\b(?:контакт\w*|телефон\w*|вотсап\w*|whatsapp|скайп\w*|skype|личк\w*|директ\w*)"))
ADVICE_LEMMAS = frozenset("советовать посоветовать рекомендовать порекомендовать предлагать предложить желать "
                          "пожелать призывать призвать просить попросить".split())
_ALPHA_WORD = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")


def v5_mask(norm: str) -> str:
    """Фраза без пустых формул, шаблонов gigachat и рамки модели: что останется — её содержание."""
    s = re.sub(FORMULA_CLAUSE_RX, " ", norm, flags=re.I)
    s = re.sub(FORMULA_WORDS_RX, " ", s, flags=re.I)
    s = re.sub(TEMPLATE_RX, " ", s, flags=re.I)
    s = re.sub(PROMO_CALL_RX, " ", s, flags=re.I)
    for p in (FRAME_V5_RX, HONESTY_RX, OPEN_ADDRESS_RX, OPEN_ANNOUNCE_RX, ANNOUNCE_RX):
        s = re.sub(p, " ", s, flags=re.I)
    return s


def _content_toks(text: str) -> list[tk.Tok]:
    return [t for t in (tk.make_tok(x) for x in tk.tokenize(text)) if tk.is_content(t) and _ALPHA_WORD.fullmatch(t.text)]


def _has_formula(norm: str) -> bool:
    return bool(re.search(FORMULA_CLAUSE_RX, norm, re.I) or re.search(FORMULA_WORDS_RX, norm, re.I))


def _tail_lines(text: str) -> set[str]:
    """Хвост ответа модели: строки после последнего разделителя «---», если их не больше трёх."""
    raw = (text or "").replace("\r\n", "\n").split("\n")
    idx = [k for k, l in enumerate(raw) if SEPARATOR_RX.match(l)]
    if not idx:
        return set()
    after = [l.strip() for l in raw[idx[-1] + 1:] if l.strip()]
    return set(after) if 0 < len(after) <= 3 else set()


@dataclass
class DraftLabel:
    i: int
    text: str
    label: str            # «М», «А?», «вопрос», «след», «заголовок»; с источником — «И» вместо «А?»
    kind: str = ""        # для М: формула, повтор, рамка, обёртка, хвост
    new: list = field(default_factory=list)
    final: bool = False


def draft_labels(base: tk.Doc, prov: "Prov | None" = None) -> list[DraftLabel]:
    """Метки владельцев фраз черновика (SKILL v5, шаг 2). Без источника: М — пустая формула, рамка, повтор,
    обёртка, хвост; А? — фраза с содержательными леммами, которых нет в остальном тексте (может быть словами
    автора); вопрос — вопрос читателю; след — «заранее спасибо», «всем добра», «Источник:»; заголовок — строка-
    заголовок. С источником (prov.distinct) «А?» заменяется на «И», если у фразы опора в источнике, иначе — М."""
    heads = {t.strip() for _, t in heading_lines(base.text)}
    tail = _tail_lines(base.text)
    lines = [l for l, _ in base.lines]
    allk = [{v for t in s.words for v in tk.tok_variants(t)} for s in base.sents]
    ids = content_sent_ids(base)
    first = ids[0] if ids else None
    with_src = prov is not None and prov.distinct and prov.ref is not None
    out: list[DraftLabel] = []
    for i, s in enumerate(base.sents):
        raw_line = lines[s.line].strip() if s.line < len(lines) else ""
        rest: set = set()
        for j, k in enumerate(allk):
            if j != i:
                rest |= k
        masked = v5_mask(s.norm)
        mc = _content_toks(masked)
        new = [t for t in mc if not (tk.tok_variants(t) & rest)]
        if _has_formula(s.norm):
            new = [t for t in new if tk.word_key(t) not in FORMULA_GENERIC]
        kind = ""
        if raw_line in heads:
            lab = "заголовок"
        elif raw_line in tail:
            lab, kind = "М", "хвост"
        elif rx(WRAPPER_RX).search(s.norm):
            lab, kind = "М", "обёртка"
        elif rx(TRACE_PHRASE_RX).search(s.norm):
            lab = "след"
        elif _is_question(s) and not (i == first and rx(HOOK_RX).search(s.norm)) and not _on_list_line(base, s):
            lab = "вопрос"
        elif not new:
            lab = "М"
            kind = "формула" if _has_formula(s.norm) else ("рамка" if len(_content_toks(s.norm)) > len(mc) else "повтор")
        else:
            lab = "А?"
        if with_src and lab in ("А?", "вопрос"):
            if not prov.sent_backed(s):
                lab, kind = "М", "нет в источнике"
            elif lab == "А?":
                lab = "И"
        out.append(DraftLabel(i, s.raw.strip(), lab, kind, [t.text for t in new]))
    # зона концовки: последние FINAL_SENTS фраз с содержанием (не М, не след, не заголовок) и их абзац
    tail_ids = [d.i for d in out if d.label in ("А?", "И", "вопрос")]
    if tail_ids:
        last = tail_ids[-FINAL_SENTS:]
        para = base.sents[last[-1]].para
        zone = set(last) | {d.i for d in out if d.label in ("А?", "И", "вопрос") and base.sents[d.i].para == para}
        for d in out:
            d.final = d.i in zone
    return out


def _res_keys(res_text: str) -> set:
    """Ключи результата вместе с хэштегами и @-подписями как словами («#робопёс» ~ «робопёс»)."""
    return tk.all_keys(tk.Doc(re.sub(r"[#@]", " ", res_text or "")))


def _ckeys(s: tk.Sent) -> set:
    return {v for t in s.words if tk.is_content(t) for v in tk.tok_variants(t)}


def _question_kept(s: tk.Sent, res: tk.Doc) -> bool:
    """Вопрос черновика остался вопросом: в результате есть вопрос с половиной его знаменательных слов."""
    rq = [x for x in res.sents if _is_question(x)]
    toks = [t for t in s.words if tk.is_content(t)]
    if not toks:
        return bool(rq)
    for x in rq:
        kx = _ckeys(x)
        if sum(1 for t in toks if tk.tok_variants(t) & kx) / len(toks) >= 0.5:
            return True
    return False


def _norm_url(u: str) -> str:
    return re.sub(r"[).,;:!?»\]*_]+$", "", u.lower()).rstrip("/")


def platform_traces(base_text: str, res_text: str, ref_text: str | None = None) -> list[str]:
    """Следы площадки черновика, которых нет в результате: хэштеги, @-подписи, e-mail, ссылки, упоминание ссылки,
    ника и контактов, «заранее спасибо», «всем добра», «комментарии для минусов», «Источник:». С источником (ref_text)
    считаются только следы, которые есть и в источнике или материале."""
    lost = []
    ref_low = tk.fold_yo(ref_text.lower()) if ref_text is not None else None

    def in_ref(x: str) -> bool:
        return ref_low is None or tk.fold_yo(x.lower()) in ref_low

    for name, r in (("хэштег", tk.HASHTAG_RX), ("подпись", tk.MENTION_RX), ("e-mail", tk.EMAIL_RX)):
        a = {m.lower() for m in r.findall(base_text)}
        b = {m.lower() for m in r.findall(res_text)}
        lost += [f"{name} {x}" for x in sorted(a - b) if in_ref(x)]
    a = {_norm_url(u): u for u in tk.URL_RX.findall(base_text)}
    b = {_norm_url(u) for u in tk.URL_RX.findall(res_text)}
    lost += [f"ссылка {a[k]}" for k in sorted(set(a) - b) if in_ref(k)]
    bl, rl = tk.fold_yo(base_text.lower()), tk.fold_yo(res_text.lower())
    for name, p in CONTACT_CLASSES:
        if re.search(p, bl) and not re.search(p, rl):
            if name == "ссылка" and tk.URL_RX.search(res_text):
                continue
            if ref_low is not None and not re.search(p, ref_low):
                continue
            lost.append(f"упоминание: {name}")
    for m in re.finditer(TRACE_PHRASE_RX, bl, re.I | re.M):
        ph = m.group(0).strip()
        if ph and ph not in rl and in_ref(ph):
            lost.append(f"«{ph}»")
    if PLACEHOLDER_RX.search(base_text) and not (tk.URL_RX.search(res_text) or re.search(r"ссылк|линк", rl)):
        if ref_low is None or re.search(r"ссылк|линк|https?://", ref_low):
            lost.append("строка со ссылкой (ссылка-заглушка черновика)")
    return list(dict.fromkeys(lost))


def _imperative(t: tk.Tok, prev_low: str) -> bool:
    """Повелительное наклонение: «думайте», «просмотрите» (у «просмотрите» первый разбор — будущее время)."""
    if t.w is None or t.w.pos != "VERB" or prev_low in ("вы", "ты"):
        return False
    if "impr" in t.w.tags:
        return True
    m = tk.analyzer()
    return m is not None and any("impr" in p.tag for p in m.parse(t.low)[:3])


def _action_toks(s: tk.Sent, masked: str | None = None) -> list[tk.Tok]:
    """Глаголы действия и совета во фразе: повелительное, «советую», «рекомендую», «желаю», «прошу». С masked —
    только те, что остались после снятия рамки и формул."""
    low_mask = tk.fold_yo(masked.lower()) if masked is not None else None
    out, prev = [], ""
    for t in s.words:
        p0, prev = prev, t.low
        if t.w is None:
            continue
        adv = t.w.lemma in ADVICE_LEMMAS and t.w.pos == "VERB" and "1per" in t.w.tags
        if not (adv or _imperative(t, p0)):
            continue
        if low_mask is not None and not re.search(rf"(?<!\w){re.escape(t.low)}(?!\w)", low_mask):
            continue
        out.append(t)
    return out


def lost_actions(base: tk.Doc, labels: list[DraftLabel], rkeys: set, res: tk.Doc | None = None,
                 pairs: set | None = None) -> list[tuple[str, int]]:
    """Действие или совет черновика, которого нет в результате: «Просмотрите памятку до конца» → «В памятке указаны
    шаги». Призывы рамки промо («Переходите», «Читайте», «Посетите») и пустые формулы («Подписывайтесь») не в счёт.
    Синоним («сделайте план» → «набросайте план») не потеря: в парной фразе результата столько же глаголов действия."""
    out = []
    by_src: dict[int, set] = {}
    for i, j in (pairs or set()):
        by_src.setdefault(i, set()).add(j)
    for d in labels:
        if d.label in ("М", "заголовок"):
            continue
        s = base.sents[d.i]
        acts = _action_toks(s, v5_mask(s.norm))
        miss = [t for t in acts if not (tk.tok_variants(t) & rkeys)]
        if not miss:
            continue
        if res is not None and d.i in by_src:
            kept = sum(len(_action_toks(res.sents[j])) for j in by_src[d.i])
            if kept >= len(acts):
                continue
        out += [(t.text, d.i) for t in miss]
    return out


def block_v5(res: tk.Doc, base: tk.Doc, prov: "Prov", mode: str, res_text: str) -> tuple[list[Finding], dict]:
    """E8–E13 (v5): снятые фразы с содержанием, следы площадки, действия, оценки, слова сохранённых фраз, метки."""
    out: list[Finding] = []
    with_src = prov.distinct and prov.ref is not None
    labels = draft_labels(base, prov)
    rkeys = _res_keys(res_text)
    pairs = tk.strong_pairs(base, res)
    paired = {i for i, _ in pairs}
    removed_m, e8 = [], []
    for d in labels:
        s = base.sents[d.i]
        if d.label in ("А?", "И"):
            new = [t for t in _content_toks(v5_mask(s.norm)) if t.text in d.new]
            miss = [t.text for t in new if not (tk.tok_variants(t) & rkeys)]
            if d.i not in paired and new and len(miss) >= max(1, math.ceil(len(new) / 2)):
                e8.append((d, ", ".join(miss[:6])))
        elif d.label == "вопрос":
            if not _question_kept(s, res):
                e8.append((d, "вопрос читателю"))
        elif d.label == "М":
            allc = _content_toks(s.norm)
            miss = [t for t in allc if not (tk.tok_variants(t) & rkeys)]
            if d.kind in ("хвост", "обёртка"):
                if tk.fold_yo(s.norm.strip().lower()) not in tk.fold_yo(res.norm.lower()):
                    removed_m.append(d)
            elif d.i not in paired and (not allc or len(miss) >= max(1, math.ceil(len(allc) / 2))):
                removed_m.append(d)
    owner = "фраза с опорой в источнике (И)" if with_src else "А? — может быть словами автора"
    hard8 = [(d, m) for d, m in e8 if d.final or d.label == "вопрос"]
    soft8 = [(d, m) for d, m in e8 if not (d.final or d.label == "вопрос")]
    if hard8:
        out.append(Finding("E", "E8", "Снята концовка или вопрос с содержанием", "hard",
                           f"{len(hard8)}: {owner}; " + "; ".join(f"нет «{m}»" for _, m in hard8[:4]),
                           [_fr("черновик", d.text, m) for d, m in hard8][:MAX_FRAGS],
                           "Не удалять: вернуть фразу и, если нужно, упростить — снять формулу («Таким образом», "
                           "«Вывод простой:»), шаблон и «!», но оставить действие, утверждение или вопрос. "
                           "Удалять можно только пустые формулы («Будем рады», «Подписывайтесь», «Удачи!», "
                           "благодарность за внимание)."))
    if soft8:
        out.append(Finding("E", "E8", "Снята фраза с содержанием", "soft",
                           f"{len(soft8)}: {owner}; " + "; ".join(f"нет «{m}»" for _, m in soft8[:4]),
                           [_fr("черновик", d.text, m) for d, m in soft8][:MAX_FRAGS],
                           "Без источника снимается только рамка модели: формулы, повторы, обёртка. Если это "
                           "пересказ другими словами — оставить; если фраза пропала — вернуть или упростить."))
    # E9: следы площадки
    tr = platform_traces(base.text, res_text, prov.ref.text if with_src else None)
    if tr:
        out.append(Finding("E", "E9", "Следы площадки потеряны", "hard", ", ".join(tr[:10]),
                           hint="Хэштеги, @-подписи, ссылки, упоминание ссылки и контактов, «заранее спасибо», «всем "
                                "добра» — часть текста автора: вернуть как было. Ссылку-заглушку не вставлять, а "
                                "оставить словами («Статья по ссылке.») и написать в заметке, что ссылку нужно "
                                "поставить."))
    # E10: действие или совет
    acts = lost_actions(base, labels, rkeys, res, pairs)
    if acts:
        out.append(Finding("E", "E10", "Снято действие или совет", "hard",
                           ", ".join(dict.fromkeys(f"«{w}»" for w, _ in acts)),
                           [_fr("черновик", base.sents[i].raw, w) for w, i in acts][:MAX_FRAGS],
                           "Совет, просьба, пожелание или призыв с содержанием — мысль автора: оставить действие "
                           "(«Дочитайте памятку до конца»), а не превращать его в описание."))
    # E11: оценки черновика (без источника)
    if not with_src:
        ev = []
        for i, t in eval_words(base):
            s = base.sents[i]
            if any(t.low in m.group(0) for m in rx(TEMPLATE_RX).finditer(s.norm)):
                continue
            if not (tk.tok_variants(t) & rkeys):
                ev.append((i, t))
        if ev:
            out.append(Finding("E", "E11", "Сняты оценки черновика", "soft",
                               ", ".join(dict.fromkeys(f"«{t.text}»" for _, t in ev)),
                               [_fr("черновик", base.sents[i].raw, t.text) for i, t in ev][:MAX_FRAGS],
                               "Без источника оценка предмета поста («четыре потрясающих проекта») может быть словом "
                               "автора: оставить одну, снимать только повторные и каталожные эпитеты к пунктам."))
    # E12: слова сохранённых фраз (глагол, деталь), которых нет в результате — справка
    gone = []
    for d in labels:
        if d.label not in ("А?", "И", "вопрос", "след") or d.i not in paired:
            continue
        for t in _content_toks(v5_mask(base.sents[d.i].norm)):
            if t.w is not None and t.w.pos in ("VERB", "INFN") and not (tk.tok_variants(t) & rkeys):
                gone.append((t.text, d.i))
    if gone:
        out.append(Finding("E", "E12", "Пропали глаголы сохранённых фраз", "note",
                           ", ".join(dict.fromkeys(f"«{w}»" for w, _ in gone[:10]))
                           + " — сверь: синоним или потерянная деталь",
                           [_fr("черновик", base.sents[i].raw, w) for w, i in gone][:MAX_FRAGS],
                           "Убирая тире и склеивая фразы, не выбрасывай глагол, деталь или шутку: «посмотрела X — "
                           "местами смотрела зажмурившись» → «посмотрела X. Местами смотрела зажмурившись».",
                           counted=False))
    # E7 без источника: снятые фразы М — перечислить в заметке
    if removed_m and not with_src:
        out.append(Finding("E", "E7", "Снята рамка модели (М)", "note",
                           "; ".join(trim(d.text, 60) for d in removed_m[:8])
                           + " — перечислить в заметке («убрал, верни, если это твоё»)",
                           [_fr("черновик", d.text, d.kind) for d in removed_m][:MAX_FRAGS], counted=False))
    finals = [d for d in labels if d.final]
    if finals:
        out.append(Finding("E", "E13", "Метки черновика", "note",
                           ", ".join(f"{k} {v}" for k, v in Counter(d.label for d in labels).most_common())
                           + "; концовка: " + " / ".join(f"[{d.label}] {trim(d.text, 70)}" for d in finals[-3:]),
                           counted=False,
                           hint=("Фраза «А?» — может быть мыслью автора: упростить можно, удалять нельзя. "
                                 "М — рамка модели: снять и перечислить в заметке.")))
    info = {"draft_labels": [dict(label=d.label, kind=d.kind, final=d.final, text=d.text) for d in labels],
            "removed_m": [d.text for d in removed_m], "removed_content": [d.text for d, _ in e8],
            "frame_words": frame_words(base, labels, removed_m, rkeys),
            "removed_words": sum(base.sents[d.i].n_words for d in removed_m)}
    return out, info


def frame_words(base: tk.Doc, labels: list[DraftLabel], removed_m: list[DraftLabel], rkeys: set) -> int:
    """Слова рамки модели, которые можно снять из черновика (в предел сокращения 10% не идут): строки-заголовки,
    снятые фразы М, а внутри оставшихся фраз — слова формул, шаблонов, анонсов, «честно» и оценочных эпитетов,
    которых в результате нет."""
    gone = {d.i for d in removed_m}
    n = sum(base.sents[i].n_words for i in gone)
    for d in labels:
        if d.i in gone:
            continue
        s = base.sents[d.i]
        if d.label == "заголовок":
            n += s.n_words
            continue
        # слова фразы, которые снимает маска рамки (счёт по формам: «спасибо» дважды — два слова)
        masked = Counter(t.low for t in s.words)
        for t in (tk.make_tok(x) for x in tk.tokenize(v5_mask(s.norm))):
            if t.is_word and masked[t.low] > 0:
                masked[t.low] -= 1
        ev = rx(EVAL_RX + r"$")
        for t in s.words:
            frame = masked[t.low] > 0
            if frame:
                masked[t.low] -= 1
            if (frame or ev.match(t.low)) and not (tk.tok_variants(t) & rkeys):
                n += 1
    return n


LINK_NOTE_RX = r"\b(?:ссылк\w*|линк\w*)"
TAG_NOTE_RX = r"\b(?:тег\w*|хэштег\w*|хештег\w*)|(?<![\w&])#\w"


def coverage_lines(material: str, res_text: str) -> list[tuple[str, float]]:
    """Сборка: строки заметок, которых нет в тексте (меньше половины знаменательных слов строки). Строка, где автор
    обещает ссылку («дам ссылку», «подробности по ссылке») или ставит теги, найдена, только если в тексте есть ссылка
    (адрес или слово «ссылка») или хэштеги: в раунде 2 сборка v4 теряла именно такие строки (3 из 4 потерь)."""
    rkeys = _res_keys(res_text)
    rl = tk.fold_yo((res_text or "").lower())
    has_link = bool(tk.URL_RX.search(res_text or "") or re.search(LINK_NOTE_RX, rl))
    has_tags = bool(tk.HASHTAG_RX.search(res_text or ""))
    out = []
    for line in (material or "").replace("\r\n", "\n").split("\n"):
        st = re.sub(r"^\s*(?:[-*•–—▪●◦]|\d{1,2}[.)])\s+", "", line).strip()
        if not st:
            continue
        low = tk.fold_yo(st.lower())
        link_line, tag_line = bool(re.search(LINK_NOTE_RX, low)), bool(re.search(TAG_NOTE_RX, low))
        if (link_line and not has_link) or (tag_line and not has_tags):
            out.append((st, 0.0))
            continue
        toks = _content_toks(re.sub(r"[#@]", " ", st))
        if not toks:
            continue
        share = sum(1 for t in toks if tk.tok_variants(t) & rkeys) / len(toks)
        if share < COVER_SHARE and not (tag_line and has_tags):
            out.append((st, share))
    return out


def _sent_new_content(doc: tk.Doc, i: int) -> bool:
    """Во фразе после снятия формул и рамки есть знаменательные слова, которых нет в остальном тексте."""
    rest: set = set()
    for j, x in enumerate(doc.sents):
        if j != i:
            rest |= {v for t in x.words for v in tk.tok_variants(t)}
    s = doc.sents[i]
    new = [t for t in _content_toks(v5_mask(s.norm)) if not (tk.tok_variants(t) & rest)]
    if _has_formula(s.norm):
        new = [t for t in new if tk.word_key(t) not in FORMULA_GENERIC]
    return bool(new) or _is_question(s)


# --------------------------------------------------------------- блок F
def block_f(res: tk.Doc, base: tk.Doc | None, prov: Prov, mode: str, profile: str, genre: str) -> list[Finding]:
    out: list[Finding] = []
    # опора, по которой подачу можно считать авторской: текст автора (edit), материал, источник фактов.
    # Черновик модели такой опорой не бывает (старый вызов rewrite: --source черновик).
    use_ref = prov.ref is not None and (prov.distinct or prov.authored)
    ref_low = prov.ref.norm.lower() if use_ref else ""

    def in_ref(phrase: str) -> bool:
        return bool(use_ref) and tk.fold_yo(phrase.lower()) in ref_low

    # F1: концовка. v5: у gigachat — только формулы и «Теперь…»; без источника концовка с содержанием — «А?»
    #     (справка), а подсказка «снять» остаётся только для пустых формул
    hits = ending_hits(res, prov, use_ref, profile=profile if profile == "gigachat" else None)
    form, cont = [], []
    for i, k in hits:
        (cont if (prov.no_source and _sent_new_content(res, i)) else form).append((i, k))
    if form:
        sev = detector_sev("F1_ending", use_ref)
        title = ("Концовка-формула или «Теперь…»" if profile == "gigachat"
                 else "Концовка-мораль, призыв, благодарность или вопрос")
        if prov.no_source:
            hint = ("Пустую формулу («Будем рады», «Подписывайтесь», «Удачи!», «Таким образом» с пересказом, "
                    "благодарность за внимание) снять; вопрос читателю оставить.")
        else:
            hint = ("Нет у автора — снять, текст кончается последним фактом или его мыслью; есть — оставить "
                    "его словами, без обобщения.")
        out.append(Finding("F", "F1", title, sev,
                           "; ".join(f"{', '.join(k)}" for _, k in form)
                           + ("" if use_ref else " (без источника: проверь, есть ли это у автора)"),
                           [_fr("результат", res.sents[i].raw) for i, _ in form], hint))
    if cont:
        out.append(Finding("F", "F1", "Концовка с содержанием (А?)", "note",
                           "; ".join(f"{', '.join(k)}" for _, k in cont)
                           + " — без источника это может быть вывод или совет автора",
                           [_fr("результат", res.sents[i].raw) for i, _ in cont],
                           "Не удалять: можно упростить (снять формулу, шаблон, «!»), действие, утверждение и вопрос "
                           "оставить.", counted=False))
    # F2: связки-анонсы
    ann = [(s.raw, m.group(0)) for s in res.sents for m in [rx(ANNOUNCE_RX).search(s.norm.strip())]
           if m and not in_ref(m.group(0))]
    if ann:
        out.append(Finding("F", "F2", "Связки-анонсы", "soft", f"{len(ann)}",
                           [_fr("результат", t, m) for t, m in ann][:MAX_FRAGS],
                           "Снять анонс, оставить само содержание: «Важнее другое: X» → «X»."))
    # F3: лишнее пояснение
    ex = [(i, m) for i, m in explain_hits(res)
          if not (use_ref and prov.authored and (prov.share(res.sents[i]) or 0) >= 0.8)]
    if ex:
        out.append(Finding("F", "F3", "Лишнее пояснение", "soft",
                           f"{len(ex)}: пересказ уже сказанного без нового факта",
                           [_fr("результат", res.sents[i].raw, m) for i, m in ex][:MAX_FRAGS],
                           "Фразу, которая пересказывает предыдущую («то есть…», «иными словами…»), снять; "
                           "если в ней есть факт — оставить."))
    # F4: рамка промо
    parts = promo_parts(res)
    if use_ref and prov.ref is not None:
        ref_parts = promo_parts(prov.ref)
        parts = {k: v for k, v in parts.items() if k not in ref_parts}
    if len(parts) >= PROMO_MIN_PARTS:
        sev = detector_sev("F4_promo", use_ref)
        out.append(Finding("F", "F4", "Рамка промо-поста", sev, ", ".join(parts),
                           [_fr("результат", v, k) for k, v in parts.items()][:MAX_FRAGS],
                           "Вопрос-приманку → утверждение о новом; «Вы узнаете:» со списком → одна фраза; "
                           "«Переходите…!» → нейтральная строка со ссылкой или ничего. Ссылку, цену, дату не терять."))
    # F5: заглушки — жёстко в любом режиме
    ph = placeholder_hits(res)
    if ph:
        out.append(Finding("F", "F5", "Заглушки в тексте", "hard", ", ".join(dict.fromkeys(h.match for h in ph)),
                           [_fr("результат", h.text, h.match) for h in ph][:MAX_FRAGS],
                           "Заглушку в текст не ставить: строку с пустой ссылкой убрать, чего не хватает — в заметку."))
    # F6: подзаголовки и рубрики в постах и колонках до 600 слов
    if genre in ("post", "opinion") and res.n_words <= 600:
        heads = heading_lines(res.text)
        first_line = next((k for k, l in enumerate(res.text.split("\n")) if l.strip()), None)
        title = [h for h in heads if h[0] == first_line]
        inner = [h for h in heads if h[0] != first_line]
        src_heads = len(heading_lines(prov.ref.text)) if (use_ref and prov.ref is not None) else 0
        if inner and len(inner) > src_heads:
            out.append(Finding("F", "F6", "Подзаголовки в посте", "soft",
                               f"{len(inner)} в тексте до 600 слов", [_fr("результат", t) for _, t in inner][:MAX_FRAGS],
                               "Подзаголовки и рубрики заменить переходами словами и абзацами; списки — только для "
                               "шагов, расписаний и цен."))
        if title and genre == "post" and not (use_ref and src_heads):
            out.append(Finding("F", "F6", "Строка-заголовок в посте", "soft", "первая строка — заголовок",
                               [_fr("результат", title[0][1])],
                               "В посте строку-заголовок снять (в статье — обычной строкой, без формулы «Тема: как X»)."))
    # F7: шаблоны gigachat и yandex
    if profile in TEMPLATE_PROFILES:
        tp = [(s.raw, m.group(0)) for s in res.sents for m in rx(TEMPLATE_RX).finditer(s.norm)
              if not in_ref(m.group(0))]
        if tp:
            out.append(Finding("F", "F7", "Шаблоны gigachat и yandex", "soft",
                               ", ".join(dict.fromkeys(f"«{m}»" for _, m in tp)),
                               [_fr("результат", t, m) for t, m in tp][:MAX_FRAGS],
                               "Снять шаблон, если это не слова автора: «вдохновляющий пример», «новые высоты»."))
    # в edit режиме подача автора — его право: всё, что было в исходнике, уже отсеяно in_ref; остальное — мягко
    return out


# --------------------------------------------------------------- блок G: лента
OPEN_ADDRESS_RX = r"^\W*(?:привет|всем привет|здравствуйте|друзья|коллеги|дорогие|доброе утро|добрый (?:день|вечер))\b"
OPEN_ANNOUNCE_RX = (r"^\W*(?:сегодня\s+(?:я\s+)?(?:хочу|расскажу|поговорим|делюсь|покажу|разберем|рассказываем)|хочу поделиться|"
                    r"делюсь|рассказываю|представляю|встречайте|продолжаем|напоминаю|новый пост|в новом (?:посте|видео|выпуске))")
NEUTRAL_ENDINGS = frozenset({"факт", "ссылка"})


def ending_type(doc: tk.Doc) -> str:
    ids = content_sent_ids(doc)
    if not ids:
        return "пусто"
    s = doc.sents[ids[-1]]
    last_line = next((l for l, _ in reversed(doc.lines) if l.strip()), "")
    if _is_question(s):
        return "вопрос"
    if tk.URL_RX.search(last_line) or s.raw.strip().endswith(":"):
        return "ссылка"
    kinds = ending_kinds(s)
    for k, name in (("благодарность", "благодарность"), ("пожелание", "пожелание"), ("призыв", "призыв"),
                    ("итог", "мораль"), ("обобщение", "мораль")):
        if k in kinds:
            if name == "мораль" and (_sent_has_number(doc, ids[-1]) or ids[-1] in _sent_names(doc)):
                continue
            return name
    return "факт"


def opening_type(doc: tk.Doc) -> str:
    ids = content_sent_ids(doc)
    if not ids:
        return "пусто"
    s = doc.sents[ids[0]]
    t = s.norm.strip()
    if rx(OPEN_ADDRESS_RX).search(t):
        return "обращение"
    if _is_question(s):
        return "вопрос"
    if rx(OPEN_ANNOUNCE_RX).search(t):
        return "анонс"
    if any(k == "label" for k, _ in colon_kinds(s)):
        return "ярлык"
    if _ends_with(s.raw, "!"):
        return "восклицание"
    return "факт"


def read_feed(path: str, n: int = 12) -> list[tuple[str, str]]:
    """Последние n постов из папки: подпапки с post.txt / post.md (как posts/ проекта) или файлы .txt / .md;
    порядок — по имени (в именах дата)."""
    p = Path(path)
    items = []
    for d in sorted(x for x in p.iterdir() if x.is_dir()):
        for name in ("post.txt", "post.md", "text.txt"):
            f = d / name
            if f.exists():
                items.append((d.name, read_text(str(f))))
                break
    if not items:
        items = [(f.name, read_text(str(f))) for f in sorted(p.iterdir())
                 if f.is_file() and f.suffix.lower() in (".txt", ".md")]
    return items[-n:]


def block_g(res: tk.Doc, feed: list[tuple[str, str]]) -> tuple[list[Finding], dict]:
    out: list[Finding] = []
    seq = [(name, ending_type(tk.Doc(t)), opening_type(tk.Doc(t))) for name, t in feed]
    me_end, me_open = ending_type(res), opening_type(res)
    info = {"feed": [dict(name=n, ending=e, opening=o) for n, e, o in seq], "ending": me_end, "opening": me_open}
    ends = [e for _, e, _ in seq] + [me_end]
    opens = [o for _, _, o in seq] + [me_open]
    if len(ends) >= 3 and me_end not in NEUTRAL_ENDINGS and ends[-3:] == [me_end] * 3:
        out.append(Finding("G", "G1", "Третья концовка подряд того же типа", "soft",
                           f"«{me_end}»: " + " → ".join(f"{n} ({e})" for n, e, _ in seq[-2:]) + " → этот пост",
                           hint="Закончить последним фактом или мыслью автора; вопрос читателю — не больше двух постов подряд."))
    cnt = Counter(e for _, e, _ in seq)
    if seq:
        out.append(Finding("G", "G0", "Лента: концовки и зачины", "note",
                           f"последних постов {len(seq)}; концовки: " + ", ".join(f"{k} {v}" for k, v in cnt.most_common())
                           + "; зачины: " + ", ".join(f"{k} {v}" for k, v in Counter(o for _, _, o in seq).most_common())
                           + f"; этот пост: концовка «{me_end}», зачин «{me_open}»", counted=False))
    if len(opens) >= 3 and me_open not in ("факт",) and opens[-3:] == [me_open] * 3:
        out.append(Finding("G", "G2", "Третий зачин подряд того же типа", "note", f"«{me_open}»", counted=False,
                           hint="Начать с факта или сцены, а не с той же формулы."))
    return out, info



# =============================================================================== отчёт
@dataclass
class Report:
    mode: str
    profile: str
    genre: str
    result_file: str
    source_file: str | None
    stats: dict
    findings: list
    warnings: list
    skipped: list
    hard: int = 0
    soft: int = 0
    passed: bool = True
    draft_file: str | None = None
    material_file: str | None = None
    provenance: dict = field(default_factory=dict)
    feed: dict = field(default_factory=dict)


def _m_cut(base: tk.Doc, res: tk.Doc, prov: Prov) -> bool:
    """Из черновика вырезана фраза М: у неё нет пары в результате, а сама она без опоры в источнике (v4) или,
    без источника, это ход подачи (концовка, рамка промо, анонс, лишнее пояснение, шаблон)."""
    paired = {i for i, _ in tk.strong_pairs(base, res)}
    gone = [i for i in range(len(base.sents)) if i not in paired and base.sents[i].words]
    if not gone:
        return False
    if prov.distinct and prov.ref is not None:
        for i in gone:
            sh = prov.share(base.sents[i])
            if sh is not None and sh < M_SHARE:
                return True
    flagged = {i for i, _ in ending_hits(base)} | {i for i, _ in explain_hits(base)}
    for i in gone:
        s = base.sents[i]
        if rx(ANNOUNCE_RX).search(s.norm.strip()) or rx(TEMPLATE_RX).search(s.norm) or rx(PROMO_CALL_RX).search(s.norm):
            flagged.add(i)
    return any(i in flagged for i in gone)


def run(result_text: str, source_text: str | None = None, mode: str = "rewrite", profile: str = "core",
        genre: str = "post", result_file: str = "", source_file: str | None = None, *,
        draft_text: str | None = None, material_text: str | None = None, feed: list | None = None,
        assemble: bool = False, source_kind: str | None = None, draft_file: str | None = None,
        material_file: str | None = None) -> Report:
    """Старый вызов run(result, source, mode, …) работает как в v3: source — исходник правки (черновик или текст
    автора). v4: draft_text — черновик модели (тогда source_text — источник фактов), material_text — дословные
    сообщения автора, feed — [(имя, текст)] последних постов, assemble — сборка из слов автора (режим write)."""
    if assemble:
        mode = "write"
    res = tk.Doc(result_text)
    warnings = list(tk.dependency_warnings())
    findings: list[Finding] = []
    # исходник правки (A, B) и опора провенанса (E, F)
    if draft_text is not None and mode != "write":
        base_text = draft_text
        distinct = source_text is not None or material_text is not None
        ref_text = source_text
        if not distinct:
            ref_text = draft_text            # без источника: E и F считают М относительно черновика
            warnings.append("есть --draft, но нет --source и --material: провенанс считается по черновику, "
                            "оценки и концовки черновика по источнику не проверяются (SKILL v4, шаг 2 п. 3).")
    else:
        base_text = source_text if mode != "write" else None
        ref_text = source_text
        distinct = mode == "write" and (source_text is not None or material_text is not None)
    authored = mode == "edit" or source_kind == "dictation" or (material_text is not None and source_text is None)
    base = tk.Doc(base_text) if base_text is not None else None
    prov = Prov.build(ref_text, material_text, distinct, authored)
    a_src = base if base is not None else (prov.ref if mode == "write" else None)
    if base is not None and prov.ref is not None:
        prov.m_cut = _m_cut(base, res, prov)
    # v5: метки черновика (М / А? / вопрос / след), снятые фразы с содержанием, следы площадки, действия
    v5_find: list[Finding] = []
    if base is not None and mode == "rewrite" and prov.ref is not None and not prov.authored:
        prov.no_source = not prov.distinct
        v5_find, prov.v5 = block_v5(res, base, prov, mode, result_text)
    elif base is not None and mode == "edit":
        tr = platform_traces(base.text, result_text)
        if tr:
            v5_find.append(Finding("E", "E9", "Следы площадки потеряны", "hard", ", ".join(tr[:10]),
                                   hint="Хэштеги, @-подписи, ссылки и «заранее спасибо» в тексте автора — его: вернуть."))
    if a_src is not None:
        findings += block_a(a_src, res, mode, prov)
        if mode != "write" and base is not None:
            findings += block_b(base, res, mode, profile)
    else:
        warnings.append("нет --source: блоки A (факт-замок) и B (след правки) пропущены.")
        if mode == "edit":
            warnings.append("режим edit без исходника: бюджеты считаются как абсолютные.")
    excl_ref = prov.ref if (prov.ref is not None and (prov.distinct or prov.authored) and mode != "edit") else None
    c_find, skipped = block_c(res, genre, profile, mode, base if mode != "write" else None, excl_ref)
    findings += c_find
    findings += block_d(res, genre, mode, base if mode != "write" else None)
    e_find, e_info = block_e(res, base, prov, mode, assemble, base_text, result_text)
    findings += e_find
    findings += v5_find
    findings += block_f(res, base, prov, mode, profile, genre)
    findings += timid_finding(e_info, findings)
    g_info: dict = {}
    if feed is not None:
        g_find, g_info = block_g(res, feed)
        findings += g_find
    # SKILL v4, самопроверка: «Исправить обязательно: A, B, жёсткие флаги E … и F. В C и D допустимо одно мягкое
    # нарушение. Мягкие флаги E и F — подсказки». Мягкие E, F, G видны в отчёте, но в счёт мягких не идут: у F1
    # точность 0,25–0,42, и в счёте он один провалил бы треть живых текстов DEV (REVIEW.md v4, сверка с v3).
    for f in findings:
        if f.block in "EFG" and f.severity == "soft":
            f.counted = False
    if skipped:
        warnings.append("без pymorphy3 пропущены счётчики: " + "; ".join(skipped))
    r = rhythm(res)
    colons = len(colon_hits(res, {"label", "reveal", "list", "speech", "service"}))
    stats = dict(words=res.n_words, sentences=r.n_sents, length_bin=length_label(res.n_words),
                 long_sentences=r.n_long, mean_sentence=round(r.mean, 1) if r.mean else None,
                 sentence_cv=round(r.cv, 2) if r.cv is not None else None,
                 colons_per_100=round(colons * 100 / res.n_words, 2) if res.n_words else 0,
                 source_words=a_src.n_words if a_src is not None else None,
                 draft_words=base.n_words if (base is not None and draft_text is not None) else None,
                 ref_words=prov.ref.n_words if prov.ref is not None else None,
                 change_share=e_info.get("change_share"),
                 morph=tk.has_morph(), razdel=tk.HAS_RAZDEL)
    rep = Report(mode, profile, genre, result_file, source_file, stats, findings, warnings, skipped,
                 draft_file=draft_file, material_file=material_file,
                 provenance=dict(distinct=prov.distinct, authored=prov.authored, m_cut=prov.m_cut,
                                 last_m=e_info.get("last_m", False), m_sentences=e_info.get("m_sentences", []),
                                 shares=e_info.get("shares", []), assemble_bigrams=e_info.get("assemble_bigrams"),
                                 cleaned=[w for w, _ in prov.cleaned], no_source=prov.no_source,
                                 draft_labels=prov.v5.get("draft_labels", []),
                                 removed_m=prov.v5.get("removed_m", []),
                                 removed_content=prov.v5.get("removed_content", []),
                                 uncovered=e_info.get("uncovered", [])),
                 feed=g_info)
    rep.hard = sum(1 for f in findings if f.severity == "hard")
    rep.soft = sum(1 for f in findings if f.severity == "soft" and f.counted)
    rep.passed = rep.hard == 0 and rep.soft <= 1
    return rep


BLOCK_TITLES = {"A": "A. Факт-замок (жёсткий: каждое нарушение — откатить правку в этом месте)",
                "B": "B. След ИИ-правки (жёсткий)",
                "C": "C. Бюджеты маркеров профиля (мягкий; жёсткие — только по стратам budgets.json)",
                "D": "D. Ритм (мягкий)",
                "E": "E. Провенанс: чьи это фразы",
                "F": "F. Подача",
                "G": "G. Лента (мягкий)"}


def render(rep: Report) -> str:
    L = []
    w = L.append
    st = rep.stats

    def v(x):
        return "—" if x is None else x
    w(f"Самопроверка pocherk v5: режим {rep.mode}, профиль {rep.profile}, жанр {GENRE_RU[rep.genre]}")
    w(f"Результат: {rep.result_file or '—'} — {st['words']} слов, {st['sentences']} фраз (корзина {st['length_bin']}); "
      f"фраз > 25 слов: {st['long_sentences']}; средняя фраза {v(st['mean_sentence'])}; CV {v(st['sentence_cv'])}; "
      f"«:» на 100 слов {st['colons_per_100']}")
    if rep.draft_file or st.get("draft_words") is not None:
        cs = st.get("change_share")
        w(f"Черновик: {rep.draft_file or '—'} — {st['draft_words']} слов; изменено слов: "
          f"{'—' if cs is None else format(cs, '.1%')}")
    if rep.source_file or st.get("ref_words") is not None:
        w(f"Исходник/источник: {rep.source_file or '—'}" + (f"; материал: {rep.material_file}" if rep.material_file else "")
          + f" — {v(st.get('ref_words'))} слов")
    for x in rep.warnings:
        w(f"[предупреждение] {x}")
    for blk in "ABCDEFG":
        fs = [f for f in rep.findings if f.block == blk]
        if blk in "AB" and st["source_words"] is None:
            w("")
            w(f"{BLOCK_TITLES[blk]} — пропущен (нет --source)")
            continue
        if blk == "B" and rep.mode == "write":
            w("")
            w(f"{BLOCK_TITLES[blk]} — не применяется в режиме write")
            continue
        if blk == "E" and st.get("ref_words") is None:
            w("")
            w(f"{BLOCK_TITLES[blk]} — пропущен (нет ни источника, ни исходника)")
            continue
        if blk == "G" and not rep.feed:
            continue
        viol = [f for f in fs if f.severity != "note"]
        notes = [f for f in fs if f.severity == "note"]
        w("")
        if blk in "AB":
            w(f"{BLOCK_TITLES[blk]} — нарушений: {len(viol)}")
        else:
            hard = sum(1 for f in viol if f.severity == "hard")
            if blk in "EFG":
                cnt = sum(1 for f in viol if f.severity == "soft")
                w(f"{BLOCK_TITLES[blk]} — " + f"жёстких: {hard}, мягких (подсказки, не в счёт): {cnt}"
                  + (f", справок: {len(notes)}" if notes else ""))
            else:
                cnt = sum(1 for f in viol if f.counted and f.severity == "soft")
                w(f"{BLOCK_TITLES[blk]} — " + (f"жёстких: {hard}, " if hard else "") + f"мягких нарушений: {cnt}"
                  + (f", подсказок: {len(notes)}" if notes else ""))
        for f in viol + notes:
            tag = {"hard": "✗", "soft": "!", "note": "·"}[f.severity] if f.counted or f.severity != "soft" else "!·"
            w(f"  {tag} [{f.code}] {f.title}: {f.message}")
            for fr in f.frags:
                m = f"  ← {fr.match}" if fr.match and fr.match not in ("?", "!", "(") else ""
                w(f"      {fr.where}: «{fr.text}»{m}")
            if f.hint and f.severity != "note":
                w(f"      как править: {f.hint}")
            elif f.hint and f.severity == "note" and f.block in "ACE":
                w(f"      подсказка: {f.hint}")
    w("")
    w("Обозначения: ✗ жёсткое нарушение; ! мягкое, идёт в счёт; !· мягкое, но не в счёт (тот же маркер или "
      "подсказка E, F, G: проверь место и реши по смыслу); · справка.")
    verdict = "ПРОЙДЕНО" if rep.passed else "НЕ ПРОЙДЕНО"
    w(f"Итог: {verdict}. Жёстких нарушений: {rep.hard}; мягких в счёт: {rep.soft}, допустимо 1. "
      f"Код выхода {0 if rep.passed else 1}.")
    if not rep.passed:
        w("Что делать: каждое жёсткое нарушение A и B — откатить правку в этом месте; жёсткие E8–E10 и E5 — вернуть "
          "снятое (концовку, вопрос, совет, хэштег, ссылку, строку заметок; упростить можно, удалять нельзя); "
          "остальные жёсткие E и F — снять фразу М, число не из источника, рамку промо или заглушку; из мягких C и D "
          "исправить всё, кроме одного. "
          "Не гнать счётчики к нулю: "
          "у 48% живых текстов есть хотя бы один такой ход.")
    return "\n".join(L)


def to_json(rep: Report) -> str:
    d = asdict(rep)
    return json.dumps(d, ensure_ascii=False, indent=1)


def read_text(path: str) -> str:
    p = Path(path)
    b = p.read_bytes()
    for enc in ("utf-8-sig", "cp1251"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", errors="replace")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Самопроверка текста по скиллу pocherk v5 (блоки A–G).")
    ap.add_argument("--result", required=True, help="файл с результатом правки")
    ap.add_argument("--source", help="источник фактов (бриф, новость, диктовка); без --draft — исходник правки, "
                                     "как в v3 (черновик в rewrite, текст автора в edit)")
    ap.add_argument("--draft", help="черновик модели (rewrite): A и B сверяются с ним, потери — по источнику")
    ap.add_argument("--material", help="дословные сообщения автора: опора для фраз от его лица (E4) и сборки (E5)")
    ap.add_argument("--source-kind", choices=("brief", "news", "dictation"),
                    help="что лежит в --source; dictation — слова автора (его концовки и рамки — А)")
    ap.add_argument("--feed", help="папка с последними постами (подпапки с post.txt или файлы .txt/.md): блок G")
    ap.add_argument("--feed-n", type=int, default=12, help="сколько последних постов брать из --feed")
    ap.add_argument("--assemble", action="store_true", help="сборка из слов автора (режим write)")
    ap.add_argument("--mode", choices=MODES, default="rewrite")
    ap.add_argument("--profile", choices=PROFILES, default="core")
    ap.add_argument("--genre", choices=GENRES, default="post")
    ap.add_argument("--json", action="store_true", help="вывести отчёт в JSON")
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass
    a = ap.parse_args(argv)
    try:
        res_text = read_text(a.result)
        src_text = read_text(a.source) if a.source else None
        draft_text = read_text(a.draft) if a.draft else None
        mat_text = read_text(a.material) if a.material else None
        feed = read_feed(a.feed, a.feed_n) if a.feed else None
    except OSError as e:
        print(f"не удалось прочитать файл: {e}", file=sys.stderr)
        return 2
    rep = run(res_text, src_text, a.mode, a.profile, a.genre, a.result, a.source, draft_text=draft_text,
              material_text=mat_text, feed=feed, assemble=a.assemble, source_kind=a.source_kind,
              draft_file=a.draft, material_file=a.material)
    print(to_json(rep) if a.json else render(rep))
    return 0 if rep.passed else 1


if __name__ == "__main__":
    sys.exit(main())
