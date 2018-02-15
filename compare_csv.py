#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2018 Pontus Lurcock
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import List, Optional
import argparse
import csv
import re
import math


class CsvComparer:

    def __init__(self, separator=","):
        self.separator = separator

    @staticmethod
    def are_equal_to_given_precision(string0: str, string1: str) -> bool:
        if string0 == string1:
            return True

        try:
            floats = [float(s) for s in (string0, string1)]
            sig_figs = [CsvComparer.sig_figs(s) for s in (string0, string1)]
        except ValueError:
            return False

        if floats[0] == floats[1]:
            # This catches the case where we're comparing -0 with 0,
            # which would otherwise return an incorrect False result.
            return True

        if math.copysign(floats[0], floats[1]) != floats[0]:
            # opposite signs (and we know they're non-zero)
            return False

        positives = [abs(x) for x in floats]

        if positives[0] >= positives[1] * 10 or \
           positives[1] >= positives[0] * 10:
            return False
        # We've now established that they have the same order of magnitude.

        digits = [CsvComparer.extract_mantissa_digits(s)
                  for s in (string0, string1)]
        digits_padded = \
            [digits[i] + ("0" * (max(sig_figs) - sig_figs[i])) for i in (0, 1)]
        max_diff = 10**(max(sig_figs) - min(sig_figs))

        ints = [int(d) for d in digits_padded]

        # This is a bit of a hack to account for the rare cases where
        # the two numbers straddle a power of ten (e.g. 9.9952E-8 vs. 1.00E-07).
        # In this case the sig. fig. counting technique puts out out by
        # an order of magnitude. We do a straightforward empirical check to
        # correct this, also checking the parsed float values to make sure
        # that we're not "correcting" a real difference in the original numbers.
        if ints[0] * 9 < ints[1] and positives[0] * 9 >= positives[1]:
            ints[0] *= 10
        if ints[1] * 9 < ints[0] and positives[1] * 9 >= positives[0]:
            ints[1] *= 10

        return abs(ints[0] - ints[1]) < max_diff

    @staticmethod
    def extract_mantissa_digits(literal: str) -> Optional[str]:
        match = re.match(r"^[-+]?([0-9]*)\.?([0-9]+)([eE][-+]?[0-9]+)?$",
                         literal)
        if match is None:
            return None
        return match.group(1) + match.group(2)

    @staticmethod
    def sig_figs(literal: str) -> int:
        match = re.match(r"^[-+]?([0-9]*)\.?([0-9]+)([eE][-+]?[0-9]+)?$",
                         literal)
        if match is None:
            return -1
        return sum([len(match.group(i)) for i in (1, 2)])

    def compare_fields(self, fields0: List[str], fields1: List[str]) ->\
            Optional[str]:
        """
        Compare two lists of strings. If they're equal, return none.
        If not, return a string describing how they differ. The definition
        of equality includes the possibility that two strings are different
        decimal representations of the same number (e.g. "3" and "3.00").
        It also includes the possibility that the strings are representations
        of two sufficiently close numbers. ("Sufficiently close" is not
        yet well-defined but will be made configurable.)

        :param fields0: a list of strings
        :param fields1: another list of strings
        :return: None if lists equal, otherwise
        """

        if len(fields0) != len(fields1):
            return "Lengths differ ({}, {})".format(len(fields0), len(fields1))

        for i in range(len(fields0)):
            if not self.are_equal_to_given_precision(fields0[i], fields1[i]):
                return "field {} differs ({}, {})".format(
                    i+1, fields0[i], fields1[i])

        return None

    def compare_linelists(self, list0: List[str], list1: List[str]) ->\
            Optional[str]:
        if len(list0) != len(list1):
            return "Unequal numbers of lines ({}, {})".\
                format(len(list0), len(list1))

        fields = []
        for line_list in list0, list1:
            fields_list = []
            fields.append(fields_list)
            reader = csv.reader(line_list,
                                delimiter=self.separator,
                                skipinitialspace=True,)
            for row in reader:
                fields_list.append(row)

        for line in range(len(fields[0])):
            result = self.compare_fields(fields[0][line], fields[1][line])
            if result is not None:
                return "On line {}: ".format(line+1)+result

        return None


def main():
    parser = argparse.ArgumentParser(description="Compare two delimited files")
    parser.add_argument("-d", "--delimiter", type=str, required=False,
                        help="delimiter between fields", default=",")
    parser.add_argument("FILE1", type=str)
    parser.add_argument("FILE2", type=str)
    args = parser.parse_args()

    with open(args.FILE1) as fh:
        lines0 = fh.readlines()

    with open(args.FILE2) as fh:
        lines1 = fh.readlines()

    separator = bytes(args.delimiter, "utf-8").decode("unicode_escape")
    comparer = CsvComparer(separator=separator)
    result = comparer.compare_linelists(lines0, lines1)
    if result is None:
        print("The files contain the same values.")
    else:
        print(result)


if __name__ == "__main__":
    main()

