#!/usr/bin/env python3
'''Copyright (C) 2017 Collabora
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Authors: Shane Fagan - shane.fagan@collabora.com
'''

import ast
import yaml

LOGIC_REPLACE = {'||': 'or',
                 '&&': 'and',
                 'true': '1',
                 'false': '0'}

KEYWORDS = ['condition', 'emit', 'delay']

def __process_rules(data):
    '''Process rule logic and turn it into ast'''
    for word in data:
        if word == "condition":
            condition = data[word][0]
            condition = ast.parse(condition).body[0]

        elif word == "emit":
            # At the moment turn them into methods, eventually
            # Swap it out with passing to the signaller
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
