"""
Unit and Integration Tests for Voice Assistant Intent Engine
Allows testing all logic offline without requiring live microphone speech.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from core.intent_engine import IntentEngine
from actions.system_actions import register_system_intents
from actions.productivity_actions import register_productivity_intents, _eval_math_ast, calculate_math
from actions.web_actions import register_web_intents
import ast


class TestIntentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = IntentEngine(fallback_handler=lambda text: f"FALLBACK: {text}")
        register_system_intents(self.engine)
        register_productivity_intents(self.engine)

    def test_time_intent(self):
        response = self.engine.process("what time is it")
        self.assertIn("The current time is", response)

    def test_date_intent(self):
        response = self.engine.process("what is today's date")
        self.assertIn("Today is", response)

    def test_math_calculation(self):
        # Test direct calculation
        res = calculate_math("calculate 25 plus 75", {})
        self.assertIn("100", res)

        res_mult = calculate_math("what is 12 multiplied by 8", {})
        self.assertIn("96", res_mult)

    def test_safe_math_ast(self):
        parsed = ast.parse("10 * (5 + 3) / 2", mode='eval')
        val = _eval_math_ast(parsed.body)
        self.assertEqual(val, 40.0)

    def test_extended_math(self):
        # Square root
        res_sqrt = self.engine.process("what is the square root of 144")
        self.assertIn("12", res_sqrt)

        # Percentage
        res_pct = self.engine.process("what is 20 percent of 150")
        self.assertIn("30", res_pct)

    def test_conversions(self):
        res_conv = self.engine.process("convert 100 celsius to fahrenheit")
        self.assertIn("212", res_conv)

    def test_quotes_facts_riddles(self):
        res_quote = self.engine.process("give me a quote")
        self.assertTrue(len(res_quote) > 10)

        res_fact = self.engine.process("tell me a fact")
        self.assertTrue("Did you know" in res_fact or len(res_fact) > 10)

        res_riddle = self.engine.process("tell me a riddle")
        self.assertTrue("Riddle:" in res_riddle or len(res_riddle) > 10)

    def test_fallback_routing(self):
        response = self.engine.process("something completely unknown and random 12345")
        self.assertTrue(response.startswith("FALLBACK:"))


if __name__ == "__main__":
    unittest.main()

