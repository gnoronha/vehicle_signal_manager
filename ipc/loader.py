#  Copyright (C) 2017, Jaguar Land Rover
#
#  This program is licensed under the terms and conditions of the
#  Mozilla Public License, version 2.0.  The full text of the 
#  Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
#

import inspect
import importlib

class LoaderError(Exception):
    """Base exception for all plugin loader errors"""
    pass

def _load_module(modulename):
    try:
        return importlib.import_module(modulename)
    except ImportError:
        raise LoaderError("error loading module: {}".format(modulename))

def _method_exists(module, method):
    return hasattr(module, method) and inspect.isroutine(getattr(module, method))

def load_plugin(modulename, use_receive=True, use_send=True):
    """
    This method will load plugin 'modulename'.

    It also offers the two optional arguments:

    use_receive: Load receive function.
    use_send:    Load send function.
    """
    # Load plugin module.
    module = _load_module(modulename)

    # Inspect caller module.
    caller_info = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_info[0])

    # Override receive/send functions.
    if use_receive:
        if _method_exists(caller_module, 'receive') and \
           _method_exists(module, 'receive'):
            caller_module.receive = module.receive
        else:
            raise LoaderError("error: missing 'receive' method")

    if use_send:
        if _method_exists(caller_module, 'send') and \
           _method_exists(module, 'send'):
            caller_module.send = module.send
        else:
            raise LoaderError("error: missing 'send' method")
