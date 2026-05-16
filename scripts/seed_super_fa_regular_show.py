#!/usr/bin/env python3
"""
Insere perguntas do Super FA (Apenas um Show / Regular Show) em `super_fa_questions`.

Uso (pasta `back/`, venv ativo, DATABASE_URL em `.env`):

    python scripts/seed_super_fa_regular_show.py

Perguntas já existentes (mesmo texto exato em `prompt`) são ignoradas.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Ordem das opções = A, B, C, D; correct_choice = letra da resposta certa.
SUPER_FA_ROWS: list[dict[str, str]] = [
    {
        "prompt": "Qual foi a pontuação de Mordecai e Rigby nos ossos quebrados contra (CGB)?",
        "option_a": "1.000.000 pontos",
        "option_b": "2.000.000 pontos",
        "option_c": "2.300.000 pontos",
        "option_d": "1.300.000 pontos",
        "correct_choice": "D",
    },
    {
        "prompt": "Qual a profissão do irmão do Fantasmão?",
        "option_a": "Bombeiro",
        "option_b": "Encanador",
        "option_c": "Policial",
        "option_d": "Empresário",
        "correct_choice": "C",
    },
    {
        "prompt": "Qual o nome da namorada do Fantasmão?",
        "option_a": "Célia",
        "option_b": "CJ",
        "option_c": "Mona",
        "option_d": "Starla",
        "correct_choice": "A",
    },
    {
        "prompt": "Qual funcionário do parque já ficou 1 ano inteiro sem tirar um dia de folga?",
        "option_a": "Musculoso",
        "option_b": "Fantasmão",
        "option_c": "Pairulito",
        "option_d": "Saltitão",
        "correct_choice": "D",
    },
    {
        "prompt": "Qual instrumento o Musculoso sabe tocar?",
        "option_a": "Trompete",
        "option_b": "Guitarra",
        "option_c": "Flauta",
        "option_d": "Vuvuzela",
        "correct_choice": "A",
    },
    {
        "prompt": (
            "O que acontece com Mordecai e o Rigby quando o Benson pede para eles "
            "comprarem um Queijo Quente de Luxo?"
        ),
        "option_a": "Eles lutam contra salsichas canibais",
        "option_b": "Eles aprendem a fazer manobras radicais com motocross",
        "option_c": "Eles viram astronautas",
        "option_d": "Eles voltam pra 1980",
        "correct_choice": "C",
    },
    {
        "prompt": "Qual o nome da ex-namorada do Saltitão?",
        "option_a": "Starla",
        "option_b": "Margaret",
        "option_c": "Eileen",
        "option_d": "Mona",
        "correct_choice": "D",
    },
    {
        "prompt": "O que o Rigby confessa para a Margaret sobre a Eileen?",
        "option_a": "Que ele é apaixonado por ela",
        "option_b": "Que ela é irritante",
        "option_c": "Que ela é chata",
        "option_d": "Que ela fica bonita sem óculos.",
        "correct_choice": "D",
    },
    {
        "prompt": "Qual o maior medo do Rigby?",
        "option_a": "A Morte",
        "option_b": "O cheiro do sovaco do Musculoso",
        "option_c": "Hamboning",
        "option_d": "Mascotes de parques temáticos",
        "correct_choice": "D",
    },
    {
        "prompt": "Em qual desses desenhos Musculoso e Fantasmão já apareceram?",
        "option_a": "O Incrível Mundo de Gumball",
        "option_b": "Titio Avô",
        "option_c": "Steven Universo",
        "option_d": "Jellystone",
        "correct_choice": "A",
    },
    {
        "prompt": "Qual o trabalho de Don, irmão do Rigby?",
        "option_a": "Contador",
        "option_b": "Chef",
        "option_c": "Engenheiro",
        "option_d": "Dublê",
        "correct_choice": "A",
    },
    {
        "prompt": (
            "Qual matéria o Cavalo Festeiro precisa de ajuda de Mordecai e Rigby para passar?"
        ),
        "option_a": "História Americana",
        "option_b": "Matemática",
        "option_c": "Biologia",
        "option_d": "Espanhol",
        "correct_choice": "A",
    },
    {
        "prompt": (
            "Quem ajuda o Mordecai quando ele tem um desentendimento com a CJ após uma confusão "
            "envolvendo a Margaret no Natal?"
        ),
        "option_a": "Rigby",
        "option_b": "Saxofonista Triste",
        "option_c": "Saltitão",
        "option_d": "Mordecai do Futuro",
        "correct_choice": "B",
    },
    {
        "prompt": "Qual desses atores famosos já fez mais de um personagem em Apenas um Show?",
        "option_a": "Tim Curry",
        "option_b": "Courteney Cox",
        "option_c": "Terry Crews",
        "option_d": "Donald Glover",
        "correct_choice": "A",
    },
    {
        "prompt": "Qual o nome do pai do Rigby?",
        "option_a": "Sherm",
        "option_b": "Carlos",
        "option_c": "Ricky",
        "option_d": "Josh",
        "correct_choice": "A",
    },
    {
        "prompt": "De que artista o personagem Gary é uma paródia?",
        "option_a": "Freddy Mercury",
        "option_b": "David Bowie",
        "option_c": "Michael Jackson",
        "option_d": "Eddie Murphy",
        "correct_choice": "B",
    },
]

CATEGORY = "Super FA"


def main() -> None:
    from app.core.database import SessionLocal, engine
    from app.model.super_fa_question import SuperFaQuestion

    if engine is None or SessionLocal is None:
        print("DATABASE_URL não configurada. Defina em back/.env")
        sys.exit(1)

    session = SessionLocal()
    try:
        existing_prompts = set(
            session.scalars(select(SuperFaQuestion.prompt)).all()
        )
        added = 0
        skipped = 0
        for d in SUPER_FA_ROWS:
            if d["prompt"] in existing_prompts:
                skipped += 1
                continue
            session.add(
                SuperFaQuestion(
                    prompt=d["prompt"],
                    option_a=d["option_a"],
                    option_b=d["option_b"],
                    option_c=d["option_c"],
                    option_d=d["option_d"],
                    correct_choice=d["correct_choice"],
                    category=CATEGORY,
                )
            )
            existing_prompts.add(d["prompt"])
            added += 1
        session.commit()
        print(f"Inseridas: {added}. Ignoradas (já existiam): {skipped}.")
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
