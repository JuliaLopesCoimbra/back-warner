import re


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_valid_cpf(digits: str) -> bool:
    """Valida CPF brasileiro (11 dígitos + dígitos verificadores). Rejeita sequências repetidas."""
    d = only_digits(digits)
    if len(d) != 11 or not d.isdigit():
        return False
    if d == d[0] * 11:
        return False
    nums = [int(c) for c in d]
    s1 = sum(nums[i] * (10 - i) for i in range(9))
    r1 = s1 % 11
    dv1 = 0 if r1 < 2 else 11 - r1
    if nums[9] != dv1:
        return False
    s2 = sum(nums[i] * (11 - i) for i in range(10))
    r2 = s2 % 11
    dv2 = 0 if r2 < 2 else 11 - r2
    return nums[10] == dv2


def normalize_cpf(value: str) -> str:
    d = only_digits(value)
    return d[:11]


def mask_cpf_show_last_three(value: str) -> str:
    """Mascara CPF para exibição pública: asteriscos + 3 últimos dígitos (ex.: ***.***.**-123)."""
    d = only_digits(value)
    if len(d) != 11:
        return "***.***.**-***"
    tail = d[8:11]
    return f"***.***.**-{tail}"
    d = only_digits(digits)[:11]
    if len(d) <= 3:
        return d
    if len(d) <= 6:
        return f"{d[:3]}.{d[3:]}"
    if len(d) <= 9:
        return f"{d[:3]}.{d[3:6]}.{d[6:]}"
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"


def format_whatsapp_br_display(digits: str) -> str:
    d = only_digits(digits)[:11]
    if len(d) == 0:
        return ""
    if len(d) <= 2:
        return f"({d}"
    if len(d) <= 6:
        return f"({d[:2]}) {d[2:]}"
    if len(d) <= 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return f"({d[:2]}) {d[2:7]}-{d[7:11]}"
