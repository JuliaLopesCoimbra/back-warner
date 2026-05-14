#!/usr/bin/env python3
"""
Insere 150 participantes de demonstração no banco.

Cada um recebe:
  - CPF válido e único (gerado a partir de uma base fixa, só para dev/demo).
  - Apelido `Demo Ranking #001` … `#150`.
  - Pontuação distinta de 150 até 1.

Com isso, no ranking e na lista de sorteio (mesma ordenação do app:
`score` DESC, `nickname` ASC) a posição 1..150 coincide com o índice
lógico: #001 tem 150 pts (1º lugar), #150 tem 1 pt (150º lugar).

Uso (pasta `back/`, venv ativo, DATABASE_URL no `.env`):

    python scripts/seed_participants.py
    python scripts/seed_participants.py --force   # remove demos anteriores e recria

Requisitos: `pip install -r requirements.txt`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import delete, func, select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

N_SEED = 150
NICKNAME_PREFIX = "Demo Ranking #"
# 9 primeiros dígitos distintos para gerar CPFs válidos (verificadores calculados).
CPF_BASE_START = 100_000_000


def _cpf_from_base9(first9: str) -> str:
    nums = [int(c) for c in first9]
    s1 = sum(nums[i] * (10 - i) for i in range(9))
    r1 = s1 % 11
    dv1 = 0 if r1 < 2 else 11 - r1
    nums10 = nums + [dv1]
    s2 = sum(nums10[i] * (11 - i) for i in range(10))
    r2 = s2 % 11
    dv2 = 0 if r2 < 2 else 11 - r2
    return first9 + str(dv1) + str(dv2)


def _build_seed_cpfs() -> list[str]:
    from app.core.phone_cpf import is_valid_cpf

    out: list[str] = []
    for i in range(N_SEED):
        first9 = str(CPF_BASE_START + i).zfill(9)
        c = _cpf_from_base9(first9)
        if not is_valid_cpf(c):
            raise RuntimeError(f"CPF inválido gerado para índice {i}: {c}")
        out.append(c)
    if len(set(out)) != N_SEED:
        raise RuntimeError("CPFs gerados não são únicos")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed 150 participantes demo (ranking/sorteio).")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove participantes com apelido 'Demo Ranking #…' e insere de novo.",
    )
    args = parser.parse_args()

    from app.core.database import SessionLocal, engine
    from app.model.participant import Participant

    if engine is None or SessionLocal is None:
        print("DATABASE_URL não configurada. Defina em back/.env")
        sys.exit(1)

    cpfs = _build_seed_cpfs()
    session = SessionLocal()
    try:
        pattern = NICKNAME_PREFIX + "%"
        existing_demo = int(
            session.scalar(
                select(func.count())
                .select_from(Participant)
                .where(Participant.nickname.like(pattern))
            )
            or 0
        )

        if existing_demo >= N_SEED and not args.force:
            print(
                f"Já existem {existing_demo} participantes demo (apelido "
                f"'{NICKNAME_PREFIX}…'). Nada a inserir. Use --force para recriar."
            )
            return

        if existing_demo > 0:
            if not args.force:
                print(
                    f"Existem {existing_demo} demos (esperado 0 ou {N_SEED}). "
                    f"Use --force para apagar os demos e inserir os {N_SEED} de novo."
                )
                sys.exit(1)
            session.execute(delete(Participant).where(Participant.nickname.like(pattern)))
            session.commit()

        # Conflito se CPF demo já existir (cadastro manual com mesmo CPF).
        for c in cpfs:
            dup = session.scalar(select(Participant).where(Participant.cpf == c).limit(1))
            if dup is not None:
                print(
                    f"CPF {c} já está cadastrado ({dup.nickname!r}). "
                    "Remova o conflito ou ajuste CPF_BASE_START no script."
                )
                sys.exit(1)

        for i in range(N_SEED):
            idx = i + 1
            session.add(
                Participant(
                    nickname=f"{NICKNAME_PREFIX}{idx:03d}",
                    cpf=cpfs[i],
                    score=N_SEED + 1 - idx,
                )
            )
        session.commit()
        print(
            f"Inseridos {N_SEED} participantes demo. "
            f"Ranking/sorteio: posição 1 = {NICKNAME_PREFIX}001 ({N_SEED} pts), "
            f"posição {N_SEED} = {NICKNAME_PREFIX}{N_SEED:03d} (1 pt)."
        )
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
