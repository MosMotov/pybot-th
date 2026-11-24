"""Focused tests for the Thai number and unit reader."""

import unittest

from bot.understanding.thai_numbers import answer


class ThaiArithmeticTests(unittest.TestCase):
    def test_arabic_digits_and_thai_operator(self):
        self.assertEqual(answer("คำนวณ 12 บวก 3 เท่าไหร่"), "คำตอบคือ 15")

    def test_find_prompt_does_not_break_har_operator(self):
        self.assertEqual(answer("หา 2 บวก 3"), "คำตอบคือ 5")

    def test_thai_number_words_and_precedence(self):
        self.assertEqual(answer("ห้าคูณหกบวกสองได้เท่าไหร่"), "คำตอบคือ 32")

    def test_thai_digits_and_division(self):
        self.assertEqual(answer("๘ หาร ๒"), "คำตอบคือ 4")

    def test_thai_digits_with_equals_question(self):
        self.assertEqual(answer("๒ บวก ๓ เท่ากับเท่าไร"), "คำตอบคือ 5")

    def test_unknown_sentence_is_ignored(self):
        self.assertIsNone(answer("วันนี้ฉันมีแมวสองตัว"))

    def test_precedence_signs_and_large_word_values(self):
        for expression, expected in [
            ("หนึ่งพันบวกสอง", "1,002"), ("(๓ บวก ๒) ยกกำลัง ๒", "25"),
            ("ลบสองคูณสาม", "-6"), ("สิบเอ็ดยกกำลังสอง", "121"),
            ("ศูนย์จุดหนึ่งบวกศูนย์จุดสอง", "0.3"), ("๒ ** ๓", "8"),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(answer(expression), "คำตอบคือ " + expected)

    def test_invalid_expressions(self):
        for expression in ("๑ หาร ๐", "๒ ^ ๙๙๙๙", "๑==๑+๒", "คำนวณ 2,3+1",
                           "หกเจ็ดบวกหนึ่ง", "๑" * 250 + "บวก 2", "สองบวกสามกิโล"):
            with self.subTest(expression=expression):
                self.assertIsNone(answer(expression))


class ThaiConversionTests(unittest.TestCase):
    def test_length_conversion(self):
        self.assertEqual(answer("5 กิโลเมตร เป็นกี่เมตร"), "5 กิโลเมตร เท่ากับ 5,000 เมตร")

    def test_word_number_mass_conversion(self):
        self.assertEqual(answer("สองกิโลกรัมเท่ากับกี่กรัม"), "2 กิโลกรัม เท่ากับ 2,000 กรัม")

    def test_temperature_conversion(self):
        self.assertEqual(answer("100 องศาฟาเรนไฮต์ เป็นกี่องศาเซลเซียส"),
                         "100 องศาฟาเรนไฮต์ เท่ากับ 37.78 องศาเซลเซียส")

    def test_conversion_without_source_value_is_ignored(self):
        self.assertIsNone(answer("กี่กิโลเมตรเท่ากับกี่เมตร"))

    def test_both_units_and_the_entire_request_must_match(self):
        for text in ("1 เมตร เป็นกี่กรัม", "รถยาว 5 เมตร และต้นไม้สูง 1 เซนติเมตร",
                     "๒ เมตร เป็นกี่เมตรต่อวินาที", "2.3.4 กรัมเป็นกี่กิโลกรัม"):
            with self.subTest(text=text):
                self.assertIsNone(answer(text))

    def test_signed_temperature_and_small_distances(self):
        self.assertIn("-40 องศาฟาเรนไฮต์", answer("-40 องศาเซลเซียสเป็นกี่องศาฟาเรนไฮต์"))
        self.assertIn("0.000001 กิโลเมตร", answer("1 มิลลิเมตรเป็นกี่กิโลเมตร"))


if __name__ == "__main__":
    unittest.main()
