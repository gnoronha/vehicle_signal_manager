#!/usr/bin/env python3
# Copyright (C) 2017 Collabora
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Authors: Shane Fagan - shane.fagan@collabora.com

import unittest
import os
import re
from sys import path
BIN_PATH = os.path.abspath(os.path.join('..', 'bin'))
path.append(BIN_PATH)
from main import process


class TestMain(unittest.TestCase):
    def setUp(self):
        print(self._testMethodName)

    def test_processor(self):
        message = "bla.bla"
        process(message, None)
        self.assertTrue(os.path.isfile("messages.log"))
        with open("messages.log", "r", encoding="utf-8") as f:
            data = f.read()
            data = data.strip("\n").split("%%")[1].lstrip()
            self.assertEqual(data, message)

        os.remove("messages.log")

if __name__ == "__main__":
    unittest.main()
