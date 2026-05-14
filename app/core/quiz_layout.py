"""Assina a ordem embaralhada das alternativas (uma rodada GET → POST)."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import time
from uuid import UUID


def sign_layout(question_id: UUID, perm: list[int], secret: str, ttl_sec: int = 7200) -> str:
    body = {"q": str(question_id), "p": perm, "exp": int(time.time()) + ttl_sec}
    raw = json.dumps(body, separators=(",", ":")).encode()
    sig = hmac.new(secret.encode(), raw, hashlib.sha256).digest()
    raw_b64 = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{raw_b64}.{sig_b64}"


def _b64pad(s: str) -> str:
    pad = 4 - len(s) % 4
    return s + ("=" * pad if pad != 4 else "")


def verify_layout(token: str, secret: str) -> tuple[UUID, list[int]]:
    try:
        raw_b64, sig_b64 = token.split(".", 1)
        raw = base64.urlsafe_b64decode(_b64pad(raw_b64))
        sig = base64.urlsafe_b64decode(_b64pad(sig_b64))
    except (ValueError, binascii.Error) as e:
        raise ValueError("token inválido") from e

    expected = hmac.new(secret.encode(), raw, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("assinatura inválida")

    try:
        body = json.loads(raw.decode())
        if int(body["exp"]) < int(time.time()):
            raise ValueError("token expirado")
        perm = list(body["p"])
        if len(perm) != 4 or sorted(perm) != [0, 1, 2, 3]:
            raise ValueError("permutação inválida")
        qid = UUID(str(body["q"]))
    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
        raise ValueError("token inválido") from e

    return qid, perm


def display_choice_to_original_letter(display_choice: str, perm: list[int]) -> str:
    """Converte a letra exibida (A–D) na tela para a letra original (A–D) no banco."""
    d = display_choice.strip().upper()
    if len(d) != 1 or d not in "ABCD":
        raise ValueError("escolha inválida")
    slot = ord(d) - ord("A")
    orig_index = perm[slot]
    return chr(ord("A") + orig_index)


def display_choice_to_option_text(display_choice: str, perm: list[int], texts: list[str]) -> str:
    """Texto da alternativa correspondente à letra exibida na tela (texts = [option_a..option_d])."""
    d = display_choice.strip().upper()
    if len(d) != 1 or d not in "ABCD":
        raise ValueError("escolha inválida")
    slot = ord(d) - ord("A")
    orig_index = perm[slot]
    return texts[orig_index][:500]
