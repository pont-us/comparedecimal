#!/usr/bin/env python3

import compare_csv
import unittest


class TestCompareCsv(unittest.TestCase):

    def setUp(self):
        self.comparer = compare_csv.CsvComparer(separator="\t")

    def test_compare_fields_equal(self):
        fields = ["one", "two", "3.5", "-10.7"]
        self.assertIsNone(
            self.comparer.compare_fields(fields, fields)
        )

    def test_compare_fields_unequal(self):
        self.assertTrue(
            isinstance(self.comparer.compare_fields(
                ["one", "two", "3.5", "-10.7"],
                ["one", "3.5", "-10.7"]), str))

    def test_compare_fields_numerically_equal(self):
        self.assertIsNone(self.comparer.compare_fields(
            ["wibble", "3.5", "-10.00000"], ["wibble", "3.500", "-10"]))

    def test_compare_fields_numerically_unequal(self):
        self.assertTrue(
            isinstance(self.comparer.compare_fields(
                ["wibble", "3.5", "-10.00000"],
                ["wibble", "3.500", "-11.00000"]), str))

    def test_compare_linelists_numerically_equal(self):
        self.assertIsNone(
            self.comparer.compare_linelists(
                ["same1", "same2\tsame2", "same\t3.00\t0", "same4\tsame4"],
                ["same1", "same2\tsame2", "same\t3.0\t0.0", "same4\tsame4"],
            ))

    def test_compare_linelists_numerically_unequal(self):
        self.assertTrue(isinstance(
            self.comparer.compare_linelists(
                ["same1", "same2\tsame2", "same\t3.1\t0", "same4\tsame4"],
                ["same1", "same2\tsame2", "same\t3.0\t0.0", "same4\tsame4"],
            ), str))

    def test_compare_linelists_modulo_quotation_marks(self):
        self.assertIsNone(
            self.comparer.compare_linelists(
                ["one\ttwo\tthree"],
                ["one\t\"two\"\tthree"]
            ))


if __name__ == "__main__":
    unittest.main()
