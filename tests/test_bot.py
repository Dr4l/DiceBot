import unittest
from unittest.mock import patch

from bot import format_result, parse_expression, roll_expression


class DiceTests(unittest.TestCase):
    def test_parses_multiple_dice_terms_and_modifier(self) -> None:
        terms, modifier = parse_expression("2d6+1d8-2")
        self.assertEqual([(term.count, term.sides) for term in terms], [(2, 6), (1, 8)])
        self.assertEqual(modifier, -2)

    def test_rolls_use_one_through_sides(self) -> None:
        with patch("bot.secrets.randbelow", side_effect=[0, 5, 2]):
            result = roll_expression("3d6")
        self.assertEqual(result.rolls, (1, 6, 3))
        self.assertEqual(result.total, 10)

    def test_rejects_invalid_or_oversized_expression(self) -> None:
        for expression in ("d0", "2d6+", "d20-1d6", "101d6", "d1000001"):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    parse_expression(expression)

    def test_formats_modifier_and_total(self) -> None:
        with patch("bot.secrets.randbelow", return_value=3):
            result = roll_expression("d6+2")
        self.assertEqual(format_result(result), "**d6+2** -> [4] +2 = **6**")


if __name__ == "__main__":
    unittest.main()