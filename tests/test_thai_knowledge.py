"""Focused tests for the small Thai fact dictionary.

The Thai adapter is deliberately kept separate from the English knowledge matcher.  These
tests exercise its public ``answer`` function so the runtime adapter can use it without
depending on the English tokenizer.
"""
import unittest

from bot.knowledge.thai import answer


class ThaiKnowledgeTests(unittest.TestCase):
    def test_capital_questions_accept_spacing_and_polite_particles(self):
        self.assertIn("กรุงเทพมหานคร", answer("เมืองหลวงของประเทศไทยคืออะไรคะ"))
        self.assertIn("โตเกียว", answer("เมืองหลวง ของ ญี่ปุ่น คืออะไรครับ"))
        self.assertIn("ปารีส", answer("ประเทศฝรั่งเศสมีเมืองหลวงชื่ออะไร"))

    def test_common_science_questions(self):
        self.assertIn("แรงโน้มถ่วง", answer("ทำไมเราจึงไม่ลอยออกจากโลก"))
        self.assertIn("กระเจิง", answer("ทำไมท้องฟ้าจึงเป็นสีฟ้า"))

    def test_cooking_question_has_actionable_timing(self):
        reply = answer("ต้มไข่ไก่กี่นาทีจึงจะสุก")
        self.assertIsNotNone(reply)
        self.assertIn("10", reply)

    def test_science_question_with_composed_thai_vowels_is_supported(self):
        self.assertIn("100", answer("น้ำเดือดที่กี่องศา"))

    def test_thai_digits_are_accepted_in_a_cooking_question(self):
        reply = answer("ต้มไข่ ๖ นาทีได้ไหม")
        self.assertIsNotNone(reply)
        self.assertIn("ยางมะตูม", reply)

    def test_unrelated_or_unsupported_questions_are_not_claimed(self):
        self.assertIsNone(answer("วันนี้อากาศเป็นอย่างไร"))
        self.assertIsNone(answer("ช่วยแปลประโยคนี้เป็นภาษาอังกฤษ"))
        self.assertIsNone(answer("ฉันอ่านเรื่องเมืองหลวงของประเทศไทย"))
        self.assertIsNone(answer("ต้มไข่ในก๋วยเตี๋ยวกี่นาที"))
        self.assertIsNone(answer("ต้มไข่ 6.5.2 นาทีได้ไหม"))
        self.assertIsNone(answer("ต้มไข่" + "๙" * 5000 + "นาทีได้ไหม"))


if __name__ == "__main__":
    unittest.main()
