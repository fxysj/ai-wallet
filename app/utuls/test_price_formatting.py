import unittest
from app.utuls.format_price_display import format_price_display  # 请替换为实际模块名


class TestPriceFormatting(unittest.TestCase):
    def test_large_numbers(self):
        """测试大于等于1的价格"""
        test_cases = [
            (1.23344, "1.23"),
            (10.5678, "10.57"),
            (100.9999, "101.00"),
            (1.00001, "1.00"),
            (1.99999, "2.00"),
        ]
        for price, expected in test_cases:
            with self.subTest(price=price):
                self.assertEqual(format_price_display(price), expected)

    def test_tenths(self):
        """测试0.1到1之间的价格"""
        test_cases = [
            (0.23673, "0.237"),
            (0.98765, "0.988"),
            (0.12345, "0.123"),
            (0.50001, "0.500"),
            (0.99999, "1.000"),
        ]
        for price, expected in test_cases:
            with self.subTest(price=price):
                self.assertEqual(format_price_display(price), expected)

    def test_hundredths(self):
        """测试0.01到0.1之间的价格"""
        test_cases = [
            (0.0324842, "0.0325"),
            (0.098765, "0.0988"),
            (0.012345, "0.0123"),
            (0.050001, "0.0500"),
            (0.099999, "0.1000"),
        ]
        for price, expected in test_cases:
            with self.subTest(price=price):
                self.assertEqual(format_price_display(price), expected)

    def test_thousandths(self):
        """测试0.001到0.01之间的价格"""
        test_cases = [
            (0.002324484, "0.00232"),
            (0.0098765, "0.00988"),
            (0.0012345, "0.00123"),
            (0.0050001, "0.00500"),
            (0.0099999, "0.01000"),
        ]
        for price, expected in test_cases:
            with self.subTest(price=price):
                self.assertEqual(format_price_display(price), expected)

    def test_ten_thousandths(self):
        """测试0.0001到0.001之间的价格"""
        test_cases = [
            (0.0003244884, "0.000324"),
            (0.00098765, "0.000988"),
            (0.00012345, "0.000123"),
            (0.00050001, "0.000500"),
            (0.00099999, "0.001000"),
        ]
        for price, expected in test_cases:
            with self.subTest(price=price):
                self.assertEqual(format_price_display(price), expected)

    def test_hundred_thousandths(self):
        """测试0.00001到0.0001之间的价格"""
        test_cases = [
            (0.0000827442, "0.0000827"),
            (0.000098765, "0.0000988"),
            (0.000012345, "0.0000123"),
            (0.000050001, "0.0000500"),
            (0.000099999, "0.0001000"),
        ]
        for price, expected in test_cases:
            with self.subTest(price=price):
                self.assertEqual(format_price_display(price), expected)

    def test_scientific_notation(self):
        """测试极小价格（使用科学记数法表示）"""
        test_cases = [
            (0.000006272482, "0.0(5)627"),
            (0.000000424349, "0.0(6)424"),
            (0.000000098765, "0.0(7)987"),
            (0.000000001234, "0.0(8)123"),
            (0.000000000567, "0.0(9)567"),
        ]
        for price, expected in test_cases:
            with self.subTest(price=price):
                self.assertEqual(format_price_display(price), expected)

    def test_special_cases(self):
        """测试特殊情况"""
        test_cases = [
            (0, "0.0"),
            (-1.2345, "-1.23"),
            (-0.0003245, "-0.000325"),
        ]
        for price, expected in test_cases:
            with self.subTest(price=price):
                self.assertEqual(format_price_display(price), expected)


if __name__ == '__main__':
    unittest.main()