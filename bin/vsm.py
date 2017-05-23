#!/usr/bin/env python3
# Copyright (C) 2017 Collabora
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Authors: Shane Fagan - shane.fagan@collabora.com

import datetime
import sys
import os
import argparse
import yaml
import glob
import ast
from time import sleep

LOGIC_REPLACE = {'||': 'or',
                 '&&': 'and',
                 'true': '1',
                 'false': '0'}

KEYWORDS = ['condition', 'emit']

class State():
    '''
        Class to handle states
    '''
    def __init__(self, conf, rules_dir):
        with open(conf) as f:
            data = yaml.load(f.read())

        for item in data:
            item = item.replace(" ", "").split("=")
            vars(self)[item[0]] = item[1]

        self.code = dict()
        for file_name in glob.glob(os.path.join(rules_dir, '*.yaml')):
            with open(file_name) as f:
                sig_name = file_name.strip(".yaml").split("/")[-1]
                self.code[sig_name] = parse_rules(f.read())


def __process_rules(data):
    '''Process rule logic and turn it into ast'''
    for word in data:
        if word == "condition":
            condition = data[word][0]
            condition = ast.parse(condition).body[0]

        elif word == "emit":
            action = "emit(\'{}\')".format(data[word]["signal"])
            action = ast.parse(action).body[0]

        else:
            print("Unhandled keyword {}".format(word))

    ifnode = ast.If(condition.value, [action], [])
    ast_module = ast.Module([ifnode])

    ast.fix_missing_locations(ast_module)

    code = compile(ast_module, '<string>', 'exec')
    return code

def parse_rules(data):
    '''
        Parse YAML rules for policy manager and return ast code.
    '''

    for key, value in LOGIC_REPLACE.items():
         data = data.replace(key, value).strip()

    data = yaml.load(data)

    code = __process_rules(data)

    return code


def emit(message):
    print(message)

def exec_code(signal):
    try:
        exec(state.code[signal])
    except Exception as e:
        print(e)

def run():
    '''
        Loop to grab logic from stdin, then spawn a threads for processing
    '''
    for line in sys.stdin:
        line = line.replace(" ", "").strip('\n')
        if line == "":
            # Ignore blank lines
            pass
        if line == "quit":
            break
        elif "=" in line:
            line = line.split("=")
            process(line[0], line[1])
        else:
            process(line, None)

def process(signal, value):
    '''
        Handle the emitting of signals and adding values to state
    '''
    # from str to int or float (if that is needed)
    if type(value) == 'str' and value.isalnum():
        if '.' in value:
            value = float(value)
        else:
            value = int(value)

    if value is not None:
        # If it's an assignment do it
        vars(state)[signal] = value
    else:
        # Else run the method
        exec_code(signal)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', type=str,
                        help='Configuration yaml file', required=True)
    parser.add_argument('--rules', type=str,
                        help='yaml rules folder', required=True)
    args = parser.parse_args()

    state = State(args.conf, args.rules)
    run()
