#!/usr/bin/python

import sys
from interpreter import vm as vm


class terminal_in:

    def __init__(self):
        self.__buffer = ""

    def cheat(self, input_str):
        def dump(args):
            self.vm.dump_state(args[1])

        commands = {'!dump': dump}
        args = input_str.split(' ')
        commands[args[0]](args)

    def get_char(self):
        if self.__buffer == "":
            user_input = '!'
            while len(user_input) > 0 and user_input[0] == '!':
                user_input = raw_input()
                if len(user_input) > 0 and user_input[0] == '!':
                    self.cheat(user_input)

            self.__buffer = user_input + "\n"
        answer = self.__buffer[0]
        self.__buffer = self.__buffer[1:]
        return answer


terminal = terminal_in()
in_fn = terminal.get_char


def terminal_out(character):
    sys.stdout.write(character)


emulator = vm(in_fn, terminal_out)

# terminal needs reference for access in cheatmode
terminal.vm = emulator

emulator.load_binary("challenge.bin")


while True:
    emulator.step()
