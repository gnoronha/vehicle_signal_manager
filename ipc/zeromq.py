#  Copyright (C) 2017, Jaguar Land Rover
#
#  This program is licensed under the terms and conditions of the
#  Mozilla Public License, version 2.0.  The full text of the 
#  Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
#

import zmq

SOCKET_ADDR="tcp://127.0.0.1:9090"

# The module public interface consists of the following functions:
#
# send    - Function to send signal.
#           It takes signal ID and value as arguments.
#
# receive - Function to receive signal.
#           It returns the received message as a tuple of (ID, Value).

def send(signal, value):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(SOCKET_ADDR)

    # Send Python tuple: (Signal ID, Signal Value).
    socket.send_pyobj((signal, value))


def receive():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(SOCKET_ADDR)

    # Receive Python object: (Signal ID, Signal Value).
    return socket.recv_pyobj()
