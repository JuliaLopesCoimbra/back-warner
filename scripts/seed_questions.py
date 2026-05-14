#!/usr/bin/env python3
"""
Popula a tabela `questions` com 150 perguntas de quiz.

Uso (na pasta `back/`, com venv ativo e DATABASE_URL no .env):

    python scripts/seed_questions.py

Requisitos: dependências instaladas (`pip install -r requirements.txt`).
Se já existirem 150 ou mais perguntas, o script não insere duplicatas.

Se existir `scripts/quiz_trivia_imported.py` (rode `import_docx_questions.py`),
o seed usa essas 150 perguntas e não gera blocos de matemática extra.
"""

from __future__ import annotations

import importlib.util
import random
import sys
from pathlib import Path

from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_trivia() -> list[dict[str, str]]:
    """Prefer `quiz_trivia_imported.py` (gerado a partir do .docx do evento), senão `quiz_trivia.py`."""
    scripts = Path(__file__).parent
    imported = scripts / "quiz_trivia_imported.py"
    if imported.exists():
        spec = importlib.util.spec_from_file_location("quiz_trivia_imported", imported)
        if spec is None or spec.loader is None:
            raise RuntimeError("Não foi possível carregar quiz_trivia_imported.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return list(mod.TRIVIA_IMPORT)
    path = scripts / "quiz_trivia.py"
    spec = importlib.util.spec_from_file_location("quiz_trivia", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar quiz_trivia.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.TRIVIA)


def _build_generated_questions(target_total: int, trivia_len: int) -> list[dict[str, str]]:
    need = max(0, target_total - trivia_len)
    rng = random.Random(42)
    out: list[dict[str, str]] = []
    for _ in range(need):
        op = rng.choice(["+", "-", "*"])
        if op == "+":
            a, b = rng.randint(3, 99), rng.randint(3, 99)
            ans = a + b
            prompt = f"Quanto é {a} + {b}?"
        elif op == "-":
            a, b = rng.randint(30, 150), rng.randint(5, 40)
            if a < b:
                a, b = b, a
            ans = a - b
            prompt = f"Quanto é {a} − {b}?"
        else:
            a, b = rng.randint(2, 14), rng.randint(2, 14)
            ans = a * b
            prompt = f"Quanto é {a} × {b}?"
        wrong: set[int] = set()
        tries = 0
        while len(wrong) < 3 and tries < 200:
            tries += 1
            delta = rng.randint(-35, 35)
            if delta == 0:
                continue
            cand = ans + delta
            if cand > 0 and cand != ans:
                wrong.add(cand)
        wrong_list = list(wrong)[:3]
        while len(wrong_list) < 3:
            wrong_list.append(ans + 50 + len(wrong_list))
        opts = [ans, *wrong_list[:3]]
        rng.shuffle(opts)
        letters = ["A", "B", "C", "D"]
        correct = letters[opts.index(ans)]
        str_opts = [str(x) for x in opts]
        out.append(
            {
                "prompt": prompt,
                "option_a": str_opts[0],
                "option_b": str_opts[1],
                "option_c": str_opts[2],
                "option_d": str_opts[3],
                "correct_choice": correct,
                "category": "Matemática",
            }
        )
    return out


def main() -> None:
    from app.core.database import SessionLocal, engine
    from app.model.question import Question

    if engine is None or SessionLocal is None:
        print("DATABASE_URL não configurada. Defina em back/.env")
        sys.exit(1)

    trivia = _load_trivia()
    if len(trivia) >= 150:
        rows = trivia[:150]
        generated = []
    else:
        generated = _build_generated_questions(150, len(trivia))
        rows = trivia + generated
    if len(rows) != 150:
        print(f"Aviso: total de linhas = {len(rows)} (esperado 150).")

    session = SessionLocal()
    try:
        existing = int(session.scalar(select(func.count()).select_from(Question)) or 0)
        if existing >= 150:
            print(f"Já existem {existing} perguntas (>= 150). Nada a inserir.")
            return
        for d in rows:
            session.add(
                Question(
                    prompt=d["prompt"],
                    option_a=d["option_a"],
                    option_b=d["option_b"],
                    option_c=d["option_c"],
                    option_d=d["option_d"],
                    correct_choice=d["correct_choice"],
                    category=d.get("category"),
                )
            )
        session.commit()
        print(
            f"Inseridas {len(rows)} perguntas "
            f"(trivia: {len(trivia)}, geradas matemática: {len(generated)})."
        )
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
