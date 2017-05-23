#!/usr/bin/env python3
# Copyright (C) 2017 Collabora
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Authors: Shane Fagan - shane.fagan@collabora.com

import unittest
from glob import glob
from sys import path
import os
from queue import Queue

BIN_PATH = os.path.abspath(os.path.join('..', 'bin'))
path.append(BIN_PATH)
RULES_PATH = os.path.abspath(os.path.join('..', 'sample_rules'))
from rule_parser import parse_rules


def emit(message):
    print(message)
    q.put_nowait(message)


class Main:
    '''Simple car class for testing'''
    def __init__(self):
        self.moving = True
        self.damage = True
        self.gear = "reverse"

    def stop(self):
        self.moving = False

class TestRuleParser(unittest.TestCase):
    def setUp(self):
        print(self._testMethodName)

    def test_parser(self):
        '''Test if there is code returned'''
        with open(os.path.join(RULES_PATH, 'simple/simple0.yaml')) as f:
            data = f.read()
            code = parse_rules(data)
            if not code:
                raise("No code was returned from parsing rules")

    def test_simple0(self):
        '''Test simple rules and methods for handling signals'''
        car = Main()

        with open(os.path.join(RULES_PATH, 'simple/simple0.yaml')) as f:
            data = f.read()
            code = parse_rules(data)
            if code:
                exec(code)
                message = q.get_nowait()
                self.assertEqual(message, "car.backup")
            else:
                raise("Rule error")

    def test_simple1(self):
        car = Main()

        with open(os.path.join(RULES_PATH, 'simple/simple1.yaml')) as f:
            data = f.read()
            code = parse_rules(data)
            if code:
                exec(code)
                message = q.get_nowait()
                self.assertEqual(message, "car.stop")
            else:
                raise("Rule error")

    def test_simple2(self):
        car = Main()

        with open(os.path.join(RULES_PATH, 'simple/simple2.yaml')) as f:
            data = f.read()
            code = parse_rules(data)
            if code:
                exec(code)
                # the condition isn't met so the car should be moving
                car.moving = False
                exec(code)
                # Car should not be moving now
                message = q.get_nowait()
                self.assertEqual(message, "car.stop")
            else:
                raise("Rule error")

if __name__ == '__main__':
    q = Queue()
    unittest.main()
