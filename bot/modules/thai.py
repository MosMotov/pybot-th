"""Thai conversation rules. A turn in English can use the same name and history."""
import re
from datetime import datetime

from ..knowledge import thai as knowledge
from ..memory import name, remember
from ..understanding import thai_numbers
from ..understanding.thai_text import clean_text

# Above the English conversation rules, below the existing safety band (9000).
PRIORITY = 8999

HELP = ("ฉันช่วยจำชื่อ คำนวณ แปลงหน่วย แปลคำศัพท์ง่าย ๆ และตอบคำถามทั่วไปได้ "
        "ลองถามว่า “๒ บวก ๓ เท่ากับเท่าไร” หรือ “ต้มไข่กี่นาที”")
UNKNOWN = "ฉันยังตอบคำถามนี้ไม่ได้ ลองถามว่า “ทำอะไรได้บ้าง” เพื่อดูตัวอย่างนะ"
THAI_SCRIPT = re.compile("[ก-๛]")
GREET = re.compile(r"^(?:สวัสดี|หวัดดี|ดีจ้า|ดีครับ|ดีค่ะ|ดี$)(?:ตอนเช้า|ตอนเย็น)?"
                   r"(?:ครับผม|ครับ|ค่ะ|คะ|จ้า)?[\s,，!！]*")
INTRO = re.compile(r"(?:ชื่อ(?:ของ)?(?:ฉัน|ผม|เรา|หนู)(?:คือ|ว่า)|"
                   r"(?:ดิฉัน|ฉัน|ผม|เรา|หนู)\s*ชื่อ(?:ว่า)?|"
                   r"เรียก(?:ดิฉัน|ฉัน|ผม|เรา|หนู)ว่า)\s*"
                   r"([ก-ฮะ-ฺเ-๎a-zA-Z]+(?:[ -][ก-ฮะ-ฺเ-๎a-zA-Z]+){0,2})")
RECALL = re.compile(r"(?:(?:จำได้ไหมว่า)?(?:ดิฉัน|ฉัน|ผม|เรา|หนู)ชื่ออะไร|"
                    r"ชื่อ(?:ของ)?(?:ดิฉัน|ฉัน|ผม|เรา|หนู)(?:คือ)?อะไร|"
                    r"(?:ยัง)?จำชื่อ(?:ของ)?(?:ดิฉัน|ฉัน|ผม|เรา|หนู)(?:ได้ไหม|ได้มั้ย|ได้หรือเปล่า))")

CHAT = (
    (r"(?:คุณ)?(?:ชื่ออะไร|ชื่อว่าอะไร|คือใคร|เป็นใคร)|แนะนำตัว(?:หน่อย)?",
     "ฉันชื่อ PyBot เป็นแชตบอตที่เขียนด้วย Python"),
    (r"(?:คุณ)?(?:ทำอะไรได้บ้าง|ช่วยอะไรได้บ้าง)|(?:ขอ)?ความช่วยเหลือ|ช่วยหน่อย", HELP),
    (r"(?:คุณ)?(?:พูด|คุย|พิมพ์|เข้าใจ|ตอบ)ภาษาไทย(?:ได้)?(?:ไหม|มั้ย|หรือเปล่า)",
     "ได้เลย พิมพ์คำถามเป็นภาษาไทยได้เลยนะ"),
    (r"(?:คุณ)?(?:สบายดี(?:ไหม|มั้ย|หรือเปล่า)|เป็น(?:อย่างไร|ยังไง)บ้าง)",
     "สบายดี ขอบคุณที่ถาม แล้วคุณล่ะ เป็นยังไงบ้าง"),
    (r"(?:ขอบคุณ|ขอบใจ)(?:มาก(?:ๆ)?)?(?:นะ)?", "ยินดีเลย"),
    (r"ลาก่อน|บ๊ายบาย|บาย|ไว้(?:คุย|เจอ)กัน(?:ใหม่)?|(?:แล้ว)?พบกันใหม่",
     "แล้วพบกันใหม่นะ"),
)

WORDS = {"cat": "แมว", "dog": "สุนัข", "water": "น้ำ", "hello": "สวัสดี",
         "thank you": "ขอบคุณ", "sorry": "ขอโทษ", "goodbye": "ลาก่อน",
         "book": "หนังสือ", "rice": "ข้าว", "house": "บ้าน", "friend": "เพื่อน"}
TO_ENGLISH = {**{value: key for key, value in WORDS.items()}, "หมา": "dog"}
WEEKDAYS = ("จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์")


def _translate(text):
    question = re.sub(r"""["'“”‘’]""", "", text.casefold())
    match = re.fullmatch(r"(?:คำว่า\s*)?([a-z]+(?: [a-z]+)*)\s*(?:แปลว่าอะไร|ภาษาไทย(?:คือ|เรียกว่า)อะไร)", question)
    if match and match[1] in WORDS:
        return f"{match[1]} แปลว่า {WORDS[match[1]]}"
    match = re.fullmatch(r"(?:คำว่า\s*)?([ก-๎]+)\s*ภาษาอังกฤษ(?:เขียนว่า|เรียกว่า|คือ|พูดว่า|ว่า)?(?:อะไร|อย่างไร|ยังไง)?", question)
    if match and match[1] in TO_ENGLISH:
        return f"{match[1]} ภาษาอังกฤษคือ {TO_ENGLISH[match[1]]}"


def _personal(text, compact, memory):
    if RECALL.fullmatch(compact):
        known = name(memory)
        return f"คุณชื่อ{known}" if known else "ฉันยังไม่ทราบชื่อคุณ บอกฉันได้โดยพิมพ์ว่า “ฉันชื่อ...”"
    match = INTRO.fullmatch(text)
    if match:
        given = match[1]
        if len(given) <= 64 and not re.search(r"อะไร|ใช่ไหม|ใช่มั้ย|หรือเปล่า", given):
            remember(memory, "name", given, text)
            return f"ยินดีที่ได้รู้จัก คุณ{given}"


def respond(text, memory):
    if not isinstance(text, str) or not THAI_SCRIPT.search(text):
        return None
    line = clean_text(text)
    translation = _translate(line)
    if translation:
        return translation
    greeting = GREET.match(line)
    if greeting:
        line = line[greeting.end():]
    if greeting and not line:
        return "สวัสดี มีอะไรให้ฉันช่วยไหม"
    compact = line.replace(" ", "")
    personal = _personal(line, compact, memory)
    if personal:
        return personal
    for pattern, reply in CHAT:
        if re.fullmatch(pattern, compact):
            return reply
    if compact in ("วันนี้วันที่เท่าไร", "วันนี้วันที่เท่าไหร่", "วันนี้วันที่อะไร"):
        today = datetime.now()
        return f"วันนี้วันที่ {today.day}/{today.month}/{today.year + 543} (พ.ศ.)"
    if compact == "วันนี้วันอะไร":
        return f"วันนี้วัน{WEEKDAYS[datetime.now().weekday()]}"
    if compact in ("กี่โมงแล้ว", "ตอนนี้กี่โมง", "ตอนนี้เวลากี่โมง"):
        return f"ตอนนี้เวลา {datetime.now():%H:%M} น. ตามเวลาของเครื่อง"
    answer = thai_numbers.answer(line) or knowledge.answer(line)
    if answer:
        return answer
    # Leave an English sentence quoting Thai text to the English modules.
    if (greeting or THAI_SCRIPT.match(line) or compact.endswith(("คืออะไร", "แปลว่าอะไร"))
            or len(THAI_SCRIPT.findall(line)) > len(re.findall("[a-zA-Z]", line))):
        return UNKNOWN
    return None
