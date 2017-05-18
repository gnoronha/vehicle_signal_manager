#!/usr/bin/env python3
# Copyright (C) 2017 Collabora
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Authors: Shane Fagan - shane.fagan@collabora.com

import os
import unittest
from subprocess import Popen, PIPE
from ipc.loader import load_plugin


RULES_PATH = os.path.abspath(os.path.join('.', 'sample_rules'))

def send(signal, value):
    "Function is overriden by plugin"

def receive():
    "Function is overriden by plugin"

def format_ipc_input(data):
    return [ tuple(elm.split(' = ')) for elm in data.split('\n') ]

def format_ipc_output(data):
    return (('', '') if data == '' else tuple(data.strip().split(' = ')))


class TestVSM(unittest.TestCase):

    ipc_module = None

    def run_vsm(self, name, input_data, expected_output, use_initial=True):
        conf = os.path.join(RULES_PATH, name + '.yaml')
        initial_state = os.path.join(RULES_PATH, name + '.initial.yaml')

        cmd = ['./vsm' ]

        if use_initial and os.path.exists(initial_state):
            cmd += ['--initial-state={}'.format(initial_state)]

        cmd += [conf]
        if TestVSM.ipc_module:
            cmd += [ '--ipc-module={}'.format(TestVSM.ipc_module) ]

        if TestVSM.ipc_module:
            process = Popen(cmd)

            for signal, value in format_ipc_input(input_data):
                send(signal, value)

            # Workaround for signals expecting ''
            if expected_output == '':
                send('quit', '')

            output = receive()

            process.terminate()

            self.assertEqual(output, format_ipc_output(expected_output))
        else:
            process = Popen(cmd, stdin=PIPE, stdout=PIPE)
            output, _ = process.communicate(input=input_data.encode(), timeout=2)

            self.assertEqual(output.decode(), expected_output)

    def test_simple0(self):
        input_data = 'transmission_gear = "reverse"'
        expected_output = 'car.backup = True\n'
        self.run_vsm('simple0', input_data, expected_output)

    def test_simple0_uninteresting(self):
        input_data = 'phone_call = "inactive"'
        expected_output = ''
        self.run_vsm('simple0', input_data, expected_output)

    def test_simple2_initial(self):
        input_data = 'damage = true'
        expected_output = 'car.stop = True\n'
        self.run_vsm('simple2', input_data, expected_output)

    def test_simple2_initial_uninteresting(self):
        input_data = 'moving = false'
        expected_output = ''
        self.run_vsm('simple2', input_data, expected_output)

    def test_simple2_modify_uninteresting(self):
        input_data = 'moving = true\ndamage = true'
        expected_output = ''
        self.run_vsm('simple2', input_data, expected_output)

    def test_simple2_multiple_signals(self):
        input_data = 'moving = false\ndamage = true'
        expected_output = 'car.stop = True\n'
        self.run_vsm('simple2', input_data, expected_output, False)

    @unittest.skip("delays not yet implemented")
    def test_delay(self):
        input_data = ''
        expected_output = 'lights.external.headlights = True\n'
        # NOTE: ideally, this would ensure the delay in output
        self.run_vsm('delay', input_data, expected_output, False)

    @unittest.skip("exclusive conditions not yet implemented")
    def test_exclusive_conditions(self):
        input_data = 'remote_key.command = "unlock"\nlock_state = true\nremote_key.command = "lock"'
        expected_output = 'lock_state = False\nhorn = True\n'
        self.run_vsm('exclusive_conditions', input_data, expected_output, False)

    @unittest.skip("subclauses, arithmetic, booleans not yet implemented")
    def test_subclauses_arithmetic_booleans(self):
        input_data = 'flux_capacitor.energy_generated = 1.1\nmovement.speed = 140'
        expected_output = 'lights.external.time_travel_imminent\nlights.internal.time_travel_imminent\n'
        self.run_vsm('subclauses_arithmetic_booleans', input_data,
                expected_output, False)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVSM)
    unittest.TextTestRunner(verbosity=2).run(suite)

    TestVSM.ipc_module = 'zeromq'
    load_plugin('ipc.{}'.format(TestVSM.ipc_module))
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVSM)
    unittest.TextTestRunner(verbosity=2).run(suite)
