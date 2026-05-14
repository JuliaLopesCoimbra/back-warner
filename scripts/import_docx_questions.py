#!/usr/bin/env python3
"""
Lê um .docx de perguntas (número) enunciado + 4 alternativas.
A correta deve estar em verde no Word (cor de fonte #38761d ou #6aa84f).

Se alguma pergunta não tiver verde no XML (Word às vezes não grava), use
OVERRIDES abaixo (número da pergunta → letra A–D).

Uso:
    python scripts/import_docx_questions.py "C:\\caminho\\perguntas.docx"

Se o .docx pular somente a pergunta 96 (95 -> 97), o script insere uma 96 provisoria
(Mordecai / blue jay) e avisa no console. Corrija no Word e importe de novo.

Gera `scripts/quiz_trivia_imported.py`. O `seed_questions.py` usa esse arquivo
automaticamente se ele existir.
"""
from __future__ import annotations

import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Perguntas em que o .docx não traz w:color verde nas alternativas (conferido no material).
OVERRIDES: dict[int, str] = {
    4: "C",  # "Eureca…" — correta: Mordecai e Rigby compraram uma cueca
    33: "C",  # Primo do Saltitão — Zoa (ep. Quips / "Zoando")
}

# O .docx do evento pula de 95 para 97 (nao ha linha "96)"). Inserimos uma pergunta
# plausivel ate voce incluir a 96 oficial no Word e rodar o import de novo.
GAP_96_FALLBACK: dict[str, str] = {
    "prompt": "Mordecai e qual especie de passaro?",
    "option_a": "Corvo",
    "option_b": "Urraca-azul (blue jay)",
    "option_c": "Falcao",
    "option_d": "Canario",
    "correct_choice": "B",
    "category": "Apenas um Show",
}


def qn(tag: str) -> str:
    return f"{{{W}}}{tag}"


GREEN = {"38761d", "6aa84f"}


def run_text_and_green(r: ET.Element) -> tuple[str, bool]:
    texts: list[str] = []
    for t in r.iter(qn("t")):
        if t.text:
            texts.append(t.text)
    text = "".join(texts)
    rpr = r.find(qn("rPr"))
    if rpr is None:
        return text, False
    c = rpr.find(qn("color"))
    if c is not None:
        val = c.get(qn("val"))
        if val and val.lower() in GREEN:
            return text, True
    return text, False


def paragraph_plain_and_green(p: ET.Element) -> tuple[str, bool]:
    parts: list[str] = []
    any_green = False
    for r in p.iter(qn("r")):
        t, g = run_text_and_green(r)
        if g:
            any_green = True
        parts.append(t)
    return "".join(parts).strip(), any_green


def read_paragraphs(path: Path) -> list[tuple[str, bool]]:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    out: list[tuple[str, bool]] = []
    for p in root.iter(qn("p")):
        plain, green = paragraph_plain_and_green(p)
        if plain:
            out.append((plain, green))
    return out


def parse_questions(rows: list[tuple[str, bool]]) -> list[dict[str, str]]:
    pairs: list[tuple[int, dict[str, str]]] = []
    i = 0
    q_re = re.compile(r"^(\d+)\)\s*(.*)$")

    while i < len(rows):
        line, _ = rows[i]
        m = q_re.match(line)
        if not m:
            i += 1
            continue
        qnum = int(m.group(1))
        prompt = m.group(2).strip()
        opts: list[tuple[str, bool]] = []
        i += 1
        while i < len(rows) and len(opts) < 4:
            ol, og = rows[i]
            if q_re.match(ol):
                break
            opts.append((ol, og))
            i += 1
        if len(opts) != 4:
            raise ValueError(
                f"Pergunta {qnum}: esperadas 4 alternativas, veio {len(opts)}. "
                f"Enunciado: {prompt[:80]}…"
            )
        greens = [j for j, (_, g) in enumerate(opts) if g]
        if len(greens) == 1:
            correct_idx = greens[0]
        elif len(greens) == 0 and qnum in OVERRIDES:
            letter = OVERRIDES[qnum].upper()
            correct_idx = ord(letter) - ord("A")
            if correct_idx not in range(4):
                raise ValueError(f"Override inválido para pergunta {qnum}: {letter}")
        else:
            raise ValueError(
                f"Pergunta {qnum}: esperada 1 alternativa verde, veio {len(greens)}. "
                f"Opts: {[o[0][:40] for o in opts]}"
            )
        letters = ["A", "B", "C", "D"]
        correct_choice = letters[correct_idx]
        pairs.append(
            (
                qnum,
                {
                    "prompt": prompt,
                    "option_a": opts[0][0],
                    "option_b": opts[1][0],
                    "option_c": opts[2][0],
                    "option_d": opts[3][0],
                    "correct_choice": correct_choice,
                    "category": "Apenas um Show",
                },
            )
        )

    need = set(range(1, 151))
    got = {p[0] for p in pairs}
    missing = sorted(need - got)
    extra = sorted(got - need)
    if extra:
        raise ValueError(
            "Numeracao invalida (numeros fora de 1 a 150 ou repetidos). "
            f"Extras: {extra}"
        )
    if missing == [96]:
        print(
            "[AVISO] O documento pula da pergunta 95 para a 97. "
            "Foi inserida uma pergunta 96 provisoria (Mordecai / blue jay). "
            "Inclua a 96 oficial no Word e rode o import de novo para substituir."
        )
        pairs.append((96, dict(GAP_96_FALLBACK)))
    elif missing:
        raise ValueError(
            "O documento precisa ter as perguntas 1 a 150 sem pular (exceto a 96, "
            "tratada automaticamente se for o unico buraco). "
            f"Faltando no arquivo: {missing}."
        )

    pairs.sort(key=lambda x: x[0])
    return [d for _, d in pairs]


def render_python_list(items: list[dict[str, str]]) -> str:
    lines = [
        '"""Gerado por import_docx_questions.py — não editar à mão se for reimportar."""',
        "",
        "TRIVIA_IMPORT: list[dict[str, str]] = [",
    ]
    for d in items:
        lines.append("    {")
        for k in (
            "prompt",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_choice",
            "category",
        ):
            v = d[k]
            lines.append(f'        "{k}": {repr(v)},')
        lines.append("    },")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    docx = Path(sys.argv[1])
    if not docx.exists():
        print("Arquivo não encontrado:", docx)
        sys.exit(1)

    rows = read_paragraphs(docx)
    items = parse_questions(rows)

    out = Path(__file__).resolve().parent / "quiz_trivia_imported.py"
    out.write_text(render_python_list(items), encoding="utf-8")
    print("OK:", len(items), "perguntas salvas em", out)
    print("Depois: python scripts/seed_questions.py")


if __name__ == "__main__":
    main()
