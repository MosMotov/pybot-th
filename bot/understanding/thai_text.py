"""Normalize a Thai chat message while preserving spaces and spelling in names."""
import re
import unicodedata


_POLITE_END = re.compile(r"(?:นะครับ|นะคะ|นะค่ะ|ครับผม|ครับ|ค่ะ|คะ|จ้า|จ๊ะ|จ้ะ|\s+นะ)$")


def clean_text(text):
    line = unicodedata.normalize("NFC", text).replace("\u200b", "").replace("ํา", "ำ")
    line = " ".join(line.split()).rstrip("?!.,！？。… ")
    return _POLITE_END.sub("", line).strip()
