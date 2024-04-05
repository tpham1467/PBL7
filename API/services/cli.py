import os
from pydantic import BaseModel
from subprocess import PIPE, run

from entities.Command import CommandRequest

def out(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout

def execute_cli(commandRequest: CommandRequest):
    if 'cd' in commandRequest.command:
        cmd = commandRequest.command.split(' ')
        print(cmd)
        return os.chdir(cmd[-1])
    return out(commandRequest.command.split(' '))