import asyncio
import unittest

from services.parser_service import extract_tokens, normalize_tokens, parse_event_text


class ParserServiceTests(unittest.TestCase):
    def test_extract_and_normalize_are_separated(self):
        text = "Hoy comí arroz con pollo y una ensalada"

        extracted = extract_tokens(text)
        normalized = normalize_tokens(extracted)

        self.assertIn("hoy", extracted)
        self.assertIn("con", extracted)

        self.assertNotIn("con", normalized)
        self.assertIn("arroz", normalized)
        self.assertIn("pollo", normalized)

    def test_food_composite_detection(self):
        text = "Almorcé arroz con pollo y jugo de naranja"
        result = asyncio.run(parse_event_text(text, "food"))

        self.assertIn("items", result)
        self.assertIn("arroz con pollo", result["items"])
        self.assertIn("jugo de naranja", result["items"])

    def test_contract_is_preserved(self):
        result = asyncio.run(parse_event_text("Me siento muy bien hoy", "mood"))

        self.assertEqual(result["type"], "mood")
        self.assertIn("original", result)
        self.assertIn("tokens", result)
        self.assertIn("confidence", result)
        self.assertIn("mock", result)
        self.assertIn("score", result)


if __name__ == "__main__":
    unittest.main()
