"""Thai-language answers to common geography, science and kitchen questions."""
import re
from typing import Optional

from ..understanding.thai_text import clean_text


_THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")

_CAPITALS = (
    (("ประเทศไทย", "ไทย"), "กรุงเทพมหานคร (กรุงเทพฯ)"),
    (("ญี่ปุ่น",), "โตเกียว"),
    (("จีน",), "ปักกิ่ง"),
    (("สหรัฐอเมริกา", "อเมริกา", "สหรัฐ"), "วอชิงตัน ดี.ซี."),
    (("สหราชอาณาจักร", "อังกฤษ"), "ลอนดอน"),
    (("ฝรั่งเศส",), "ปารีส"),
    (("เยอรมนี", "เยอรมัน"), "เบอร์ลิน"),
    (("เกาหลีใต้",), "โซล"),
    (("อินเดีย",), "นิวเดลี"),
    (("ออสเตรเลีย",), "แคนเบอร์รา"),
    (("สิงคโปร์",), "สิงคโปร์"),
    (("เวียดนาม",), "ฮานอย"),
)


_CAPITAL_BY_COUNTRY = {alias: city for aliases, city in _CAPITALS for alias in aliases}
_COUNTRY = "|".join(map(re.escape, _CAPITAL_BY_COUNTRY))
_CAPITAL_FIRST = re.compile(
    rf"เมืองหลวง(?:ของ)?(?:ประเทศ)?({_COUNTRY})(?:คืออะไร|ชื่ออะไร|คือที่ไหน|อยู่ที่ไหน|ที่ไหน|คือ)?")
_COUNTRY_FIRST = re.compile(
    rf"(?:ประเทศ)?({_COUNTRY})(?:มี)?เมืองหลวง(?:คืออะไร|ชื่ออะไร|คือที่ไหน|อยู่ที่ไหน)")


def _capital(clean: str) -> Optional[str]:
    match = _CAPITAL_FIRST.fullmatch(clean) or _COUNTRY_FIRST.fullmatch(clean)
    if match:
        country = match[1]
        return f"เมืองหลวงของ{country}คือ{_CAPITAL_BY_COUNTRY[country]}"
    return None


def _boiling_egg(clean: str) -> Optional[str]:
    if re.fullmatch(r"ต้มไข่(?:ไก่)?(?:กี่นาที|นานเท่าไร|นานเท่าไหร่|นานแค่ไหน)(?:จึงจะสุก|ถึงจะสุก)?", clean):
        return "ถ้าใส่ไข่ไก่ตอนน้ำเดือด ต้มประมาณ 6–7 นาทีสำหรับไข่ยางมะตูม หรือ 10–12 นาทีสำหรับไข่สุกแข็ง แล้วแช่น้ำเย็น"
    match = re.fullmatch(r"ต้มไข่(?:ไก่)?([0-9]{1,2})นาที(?:ได้ไหม|ไหม|หรือเปล่า)?", clean)
    if not match:
        return None
    minutes = int(match[1])
    if minutes < 6:
        return "ถ้าเริ่มจับเวลาตอนใส่ไข่ลงในน้ำเดือด ไข่แดงอาจยังเหลวอยู่ ถ้าชอบไข่ยางมะตูมให้ต้มประมาณ 6–7 นาที"
    if minutes <= 7:
        return "ถ้าเริ่มจับเวลาตอนใส่ไข่ลงในน้ำเดือด 6–7 นาทีจะได้ไข่ยางมะตูม จากนั้นแช่น้ำเย็น"
    return "ถ้าอยากได้ไข่สุกแข็ง ให้จับเวลาประมาณ 10–12 นาทีตั้งแต่ใส่ไข่ลงในน้ำเดือด แล้วแช่น้ำเย็น"


def _science(clean: str) -> Optional[str]:
    if clean in ("ทำไมท้องฟ้าจึงเป็นสีฟ้า", "ทำไมท้องฟ้าเป็นสีฟ้า", "ทำไมฟ้าจึงเป็นสีฟ้า", "ทำไมฟ้าเป็นสีฟ้า"):
        return "ท้องฟ้าดูเป็นสีฟ้าเพราะโมเลกุลในอากาศกระเจิงแสงสีน้ำเงินได้มากกว่าแสงสีอื่น เมื่อมองจากพื้นดินจึงเห็นสีน้ำเงินเด่นกว่า"
    if clean in ("ทำไมเราจึงไม่ลอยออกจากโลก", "ทำไมเราไม่ลอยออกจากโลก", "ทำไมคนไม่ลอยออกจากโลก"):
        return "แรงโน้มถ่วงของโลกดึงวัตถุและคนเข้าหาศูนย์กลางโลก จึงทำให้เราไม่ลอยออกไปในอวกาศ"
    if clean in ("แรงโน้มถ่วงคืออะไร", "แรงโน้มถ่วงหมายถึงอะไร", "แรงโน้มถ่วงทำงานอย่างไร"):
        return "แรงโน้มถ่วงคือแรงดึงดูดระหว่างวัตถุ วัตถุที่มีมวลมากอย่างโลกจึงดึงเราไว้บนพื้นผิว"
    if clean in ("น้ำเดือดกี่องศา", "น้ำเดือดที่กี่องศา", "อุณหภูมิน้ำเดือดเท่าไร", "อุณหภูมิน้ำเดือดเท่าไหร่"):
        return "น้ำบริสุทธิ์เดือดที่ประมาณ 100 องศาเซลเซียสที่ระดับน้ำทะเล ความดันอากาศและความสูงทำให้อุณหภูมินี้เปลี่ยนได้"
    if clean in ("ทำไมหัวหอมทำให้ร้องไห้", "ทำไมหั่นหัวหอมแล้วร้องไห้"):
        return "เมื่อหั่นหัวหอม เซลล์ที่แตกจะปล่อยสารระเหยที่ระคายเคืองตา ดวงตาจึงสร้างน้ำตาเพื่อชะล้างสารนั้น"
    return None


def _cooking(clean: str) -> Optional[str]:
    egg = _boiling_egg(clean)
    if egg is not None:
        return egg
    if clean in ("วิธีขจัดคราบตะกรันในกาต้มน้ำ", "ล้างตะกรันกาต้มน้ำ", "กาต้มน้ำมีตะกรันทำอย่างไร"):
        return "เติมน้ำกับน้ำส้มสายชูขาวในสัดส่วนเท่า ๆ กัน ต้มแล้วทิ้งไว้ประมาณ 30 นาที จากนั้นเททิ้งและต้มน้ำสะอาดล้างอีก 2 ครั้ง"
    if clean in ("วิธีหุงข้าว", "หุงข้าวทำอย่างไร", "หุงข้าวยังไง"):
        return "ซาวข้าว เติมน้ำตามสัดส่วนของข้าว แล้วหุงจนสวิตช์ตัด จากนั้นพักข้าวไว้ 10 นาทีและใช้ทัพพีคนให้ร่วน"
    return None


def answer(text: object) -> Optional[str]:
    """Return a high-confidence Thai answer, or ``None`` when this module does not match."""
    if not isinstance(text, str) or len(text) > 512:
        return None
    clean = clean_text(text).replace(" ", "").translate(_THAI_DIGITS)
    for matcher in (_capital, _science, _cooking):
        reply = matcher(clean)
        if reply is not None:
            return reply
    return None


__all__ = ["answer"]
