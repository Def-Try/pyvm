import os

def set_name(name):
    os.environ["PYVM_RUNNER_NAME"] = name

def get_name():
    return os.environ["PYVM_RUNNER_NAME"]