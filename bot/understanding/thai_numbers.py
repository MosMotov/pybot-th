"""Read complete Thai arithmetic expressions and measurement conversions."""
import ast
import re
from decimal import Decimal
from typing import Optional

from ..knowledge.maths import _eval as evaluate_arithmetic
from .thai_text import clean_text


_DIGITS = {"ศูนย์": 0, "หนึ่ง": 1, "เอ็ด": 1, "สอง": 2, "ยี่": 2, "สาม": 3,
           "สี่": 4, "ห้า": 5, "หก": 6, "เจ็ด": 7, "แปด": 8, "เก้า": 9}
_PLACES = {"สิบ": 10, "ร้อย": 100, "พัน": 1000, "หมื่น": 10000, "แสน": 100000}
_LEXEME = "|".join(sorted((*_DIGITS, *_PLACES, "ล้าน", "จุด"), key=len, reverse=True))
_WORD_NUMBER = re.compile(rf"(?:{_LEXEME})(?:\s*(?:{_LEXEME}))*")
_THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")
_OPERATORS = {"ยกกำลัง": "**", "^": "**", "หารด้วย": "/", "หาร": "/", "÷": "/",
              "คูณด้วย": "*", "คูณ": "*", "×": "*", "บวก": "+", "ลบ": "-"}
_OPERATOR = re.compile("|".join(map(re.escape, _OPERATORS)))
_PREFIX = re.compile(r"^(?:กรุณา\s*|ช่วย\s*)?(?:คำนวณ|คำนวน|แปลง|หา(?!ร))?\s*")
_SUFFIX = re.compile(r"(?:\s*(?:เท่ากับ|ได้|เป็น)?\s*(?:เท่าไหร่|เท่าไร)|\s*=)?(?:\s*หน่อย)?$")
_LIMIT = 10 ** 15


def _under_million(words):
    total, previous_place, digit = 0, 1_000_000, None
    for word in words:
        if word in _DIGITS:
            if digit is not None:
                raise ValueError("adjacent digits in a Thai cardinal")
            digit = _DIGITS[word]
        else:
            place = _PLACES[word]
            if place >= previous_place:
                raise ValueError("Thai place values must descend")
            total += (1 if digit is None else digit) * place
            digit, previous_place = None, place
    return total + (digit or 0)


def _number_literal(match):
    words = re.findall(_LEXEME, match[0])
    fraction = ""
    if "จุด" in words:
        point = words.index("จุด")
        tail = words[point + 1:]
        if not tail or not all(word in _DIGITS for word in tail):
            raise ValueError("invalid fractional digits")
        fraction = "." + "".join(str(_DIGITS[word]) for word in tail)
        words = words[:point]
    millions = 0
    if "ล้าน" in words:
        index = words.index("ล้าน")
        millions = (_under_million(words[:index]) if index else 1) * 1_000_000
        words = words[index + 1:]
        if "ล้าน" in words:
            raise ValueError("Thai cardinal exceeds supported range")
    return str(millions + _under_million(words)) + fraction


_UNIT_DEFS = {
    # canonical label: (dimension, factor-to-base, offset-to-base)
    "มิลลิเมตร": ("length", 0.001, 0), "เซนติเมตร": ("length", 0.01, 0),
    "เมตร": ("length", 1, 0), "กิโลเมตร": ("length", 1000, 0),
    "มิลลิกรัม": ("mass", 0.001, 0), "กรัม": ("mass", 1, 0),
    "กิโลกรัม": ("mass", 1000, 0), "มิลลิลิตร": ("volume", 0.001, 0),
    "ลิตร": ("volume", 1, 0),
    "องศาเซลเซียส": ("temperature", 1, 0), "องศาฟาเรนไฮต์": ("temperature", 5 / 9, -32),
    "เคลวิน": ("temperature", 1, -273.15),
}
_UNIT_ALIASES = {
    "mm": "มิลลิเมตร", "มิล": "มิลลิเมตร", "มิลลิเมตร": "มิลลิเมตร",
    "cm": "เซนติเมตร", "เซน": "เซนติเมตร", "เซนติเมตร": "เซนติเมตร",
    "m": "เมตร", "เมตร": "เมตร", "กม": "กิโลเมตร", "กม.": "กิโลเมตร", "km": "กิโลเมตร",
    "กิโลเมตร": "กิโลเมตร", "mg": "มิลลิกรัม", "มิลลิกรัม": "มิลลิกรัม",
    "g": "กรัม", "กรัม": "กรัม", "kg": "กิโลกรัม", "กิโลกรัม": "กิโลกรัม", "กก.": "กิโลกรัม",
    "ml": "มิลลิลิตร", "มล": "มิลลิลิตร", "มิลลิลิตร": "มิลลิลิตร", "l": "ลิตร", "ลิตร": "ลิตร",
    "องศาเซลเซียส": "องศาเซลเซียส", "เซลเซียส": "องศาเซลเซียส", "°c": "องศาเซลเซียส", "c": "องศาเซลเซียส",
    "องศาฟาเรนไฮต์": "องศาฟาเรนไฮต์", "ฟาเรนไฮต์": "องศาฟาเรนไฮต์", "°f": "องศาฟาเรนไฮต์", "f": "องศาฟาเรนไฮต์",
    "เคลวิน": "เคลวิน", "k": "เคลวิน",
}

_UNIT = "|".join(map(re.escape, sorted(_UNIT_ALIASES, key=len, reverse=True)))
_CONVERSION = re.compile(
    rf"([+-]?[0-9]+(?:\.[0-9]+)?)\s*({_UNIT})\s*"
    rf"(?:เท่ากับ|เป็น|คิดเป็น|มี)?\s*(?:กี่|เท่าไร|เท่าไหร่)?\s*({_UNIT})")


def _format(value):
    # Significant digits keep tiny nonzero conversions visible without float noise.
    return format(Decimal(format(value, ".15g")), ",f")


def _convert(match):
    amount = float(match[1])
    source, target = (_UNIT_ALIASES[unit] for unit in match.group(2, 3))
    dimension, factor, offset = _UNIT_DEFS[source]
    target_dimension, target_factor, target_offset = _UNIT_DEFS[target]
    if dimension != target_dimension or abs(amount) > _LIMIT:
        return None
    value = (amount + offset) * factor / target_factor - target_offset
    if abs(value) > _LIMIT:
        return None
    if dimension == "temperature":
        value = round(value, 2)
    return f"{_format(amount)} {source} เท่ากับ {_format(value)} {target}"


def answer(text: str) -> Optional[str]:
    if not isinstance(text, str) or len(text) > 160:
        return None
    line = clean_text(text).lower().translate(_THAI_DIGITS)
    line = _SUFFIX.sub("", _PREFIX.sub("", line)).strip()
    # Strip commas only inside correctly grouped thousands.
    line = re.sub(r"(?<![0-9,])[0-9]{1,3}(?:,[0-9]{3})+(?![0-9,])",
                  lambda m: m[0].replace(",", ""), line)
    try:
        line = _WORD_NUMBER.sub(_number_literal, line)
        conversion = _CONVERSION.fullmatch(line)
        if conversion:
            return _convert(conversion)
        expr = _OPERATOR.sub(lambda m: _OPERATORS[m[0]], line)
        if not re.fullmatch(r"[0-9.()\s+*/%\-]+", expr) or not re.search(r"[+*/%\-]", expr):
            return None
        # Limit powers before handing the numeric AST to PyBot's existing evaluator.
        if expr.count("**") > 1 or len(expr) > 80:
            return None
        value = evaluate_arithmetic(ast.parse(expr, mode="eval"))
        if isinstance(value, (int, float)) and abs(value) <= _LIMIT:
            return f"คำตอบคือ {_format(value)}"
    except (ArithmeticError, SyntaxError, ValueError):
        pass
    return None
