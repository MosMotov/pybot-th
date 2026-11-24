"""Thai replies through the same module, memory and CLI used by English turns."""
import os
import subprocess
import sys
import unittest

from bot import runtime
from bot.modules import arbiter, thai


class ThaiConversation(unittest.TestCase):
    def test_common_phrases_and_normalization(self):
        for prompt, phrase in [
            ("  สวัสดี\u200bครับ！ ", "สวัสดี"),
            ("สวัสดีค่ะ สบายดีไหมคะ?", "สบายดี"),
            ("ขอบคุณมาก ๆ นะครับ!", "ยินดี"),
            ("ขอบคุณนะ", "ยินดี"),
            ("คุณชื่ออะไร", "PyBot"),
            ("คุณทำอะไรได้บ้าง", "คำนวณ"),
            ("คุยภาษาไทยได้ไหม", "ภาษาไทย"),
            ("สวัสดีนะครับ", "สวัสดี"),
            ("วันนี้วันที่เท่าไหร่คะ", "พ.ศ."),
            ("วันนี้วันอะไร", "วันนี้วัน"),
            ("กี่โมงแล้วครับ", "ตามเวลาของเครื่อง"),
            ("แล้วพบกันใหม่", "แล้วพบกัน"),
        ]:
            with self.subTest(prompt=prompt):
                self.assertIn(phrase, thai.respond(prompt, {}))

    def test_language_choice_preserves_english(self):
        for prompt in ("hello", "what does 'แมว' mean?", "My name is สมชาย", "?!", ""):
            with self.subTest(prompt=prompt):
                self.assertIsNone(thai.respond(prompt, {}))
        self.assertIn("ลองถาม", thai.respond("ดาวอังคารมีภูเขาไฟกี่ลูก", {}))
        self.assertIn("ลองถาม", thai.respond("TypeScript คืออะไร", {}))

    def test_names_and_recall_use_the_shared_store(self):
        memory = {}
        self.assertIn("น้ำฝน", thai.respond("สวัสดีค่ะ ฉันชื่อน้ำฝนค่ะ", memory))
        self.assertIn("น้ำฝน", thai.respond("จำชื่อฉันได้ไหมคะ", memory))
        self.assertIn("Alex", thai.respond("เรียกผมว่า Alex นะครับ", memory))
        self.assertIn("Alex", thai.respond("ผมชื่ออะไรครับ", memory))
        self.assertNotIn("Alex", thai.respond("ฉันชื่ออะไร", {}))
        self.assertIn("มานะ", thai.respond("ผมชื่อมานะ", {}))
        thai.respond("ผมชื่ออะไรใช่ไหม", memory)
        self.assertIn("Alex", thai.respond("ผมชื่ออะไร", memory))

    def test_translation(self):
        for question, word in [
            ("แมวภาษาอังกฤษเรียกว่าอะไร", "cat"),
            ("สวัสดีภาษาอังกฤษว่าอะไร", "hello"),
            ("hello แปลว่าอะไรครับ", "สวัสดี"),
            ('คำว่า "thank you" แปลว่าอะไร', "ขอบคุณ"),
        ]:
            self.assertIn(word, thai.respond(question, {}))

    def test_thai_routing_keeps_existing_safety_priority(self):
        candidates = [
            {"module": "safety", "priority": arbiter.SAFETY, "reply": "Safety reply"},
            {"module": "thai", "priority": thai.PRIORITY, "reply": thai.UNKNOWN},
        ]
        self.assertLess(thai.PRIORITY, arbiter.SAFETY)
        self.assertEqual(arbiter.choose("ขอความช่วยเหลือ", {}, candidates), 0)

    def test_runtime_switches_language_and_records_original_turn(self):
        memory = {}
        for text, module, phrase in [
            ("my name is Sam", None, "Sam"),
            ("ชื่อของฉันคืออะไรคะ?", "thai", "Sam"),
            ("ฉันชื่อมะลิ", "thai", "มะลิ"),
            ("what's my name?", None, "มะลิ"),
            ("๒ บวก ๓ เท่ากับเท่าไร", "thai", "5"),
            ("เมืองหลวงของญี่ปุ่นคืออะไร", "thai", "โตเกียว"),
            ("ดาวอังคารมีภูเขาไฟกี่ลูก", "thai", "ลองถาม"),
        ]:
            with self.subTest(text=text):
                result = runtime.turn(text, memory)
                self.assertIn(phrase, result["reply"])
                if module:
                    self.assertEqual(result["module"], module)
                else:
                    self.assertNotEqual(result["module"], "thai")
                self.assertEqual(memory["turns"][-1]["user"], text)

    def test_thai_cli_pipe_keeps_one_conversation(self):
        result = subprocess.run(
            [sys.executable, "-m", "pybot"], input="ฉันชื่อฟ้า\nฉันชื่ออะไรคะ\n",
            capture_output=True, encoding="utf-8", timeout=600,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.splitlines()), 2)
        self.assertIn("ฟ้า", result.stdout.splitlines()[1])
