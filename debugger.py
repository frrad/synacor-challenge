#!/usr/bin/python

import sys
from interpreter import vm as vm


class terminal:

    def __init__(self):
        self.__buffer = ""

    def get_char(self):
        if self.__buffer == "":
            user_input = '!'
            while len(user_input) > 0 and user_input[0] == '!':
                user_input = raw_input()
                if len(user_input) > 0 and user_input[0] == '!':
                    self.debugger.process_command(user_input)

            self.__buffer = user_input + "\n"
        answer = self.__buffer[0]
        self.__buffer = self.__buffer[1:]
        return answer

    def print_char(self, character):
        sys.stdout.write(character)
        if self.debugger.is_debugging():
            sys.stdout.write('\n')


class debugger:

    def __init__(self, vm):
        self.vm = vm
        self.__function_names = {}
        with open('notes/functions.txt', 'r') as f:
            for line in f:
                if len(line) == 0 or line[0] == '#' or line == '\n':
                    continue
                a = line.strip().split(':')
                self.__function_names[int(a[0])] = a[1]

        self.__call_stack = []
        self.__debugging = False
        self.op_names = {0: ['halt', 0],
                         1: ['set ', 2],
                         2: ['push', 1],
                         3: ['pop ', 1],
                         4: ['eq  ', 3],
                         5: ['gt  ', 3],
                         6: ['jmp ', 1],
                         7: ['jt  ', 2],
                         8: ['jf  ', 2],
                         9: ['add ', 3],
                         10: ['add ', 3],
                         11: ['mod ', 3],
                         12: ['and ', 3],
                         13: ['or  ', 3],
                         14: ['not ', 2],
                         15: ['rmem', 2],
                         16: ['wmem', 2],
                         17: ['call', 1],
                         18: ['ret ', 0],
                         19: ['out ', 1],
                         20: ['in  ', 1],
                         21: ['noop', 0]}

    def process_command(self, input_str):
        def dump(args):
            self.vm.dump_state(args[1])

        def start(args):
            self.__debugging = True

        def stop(args):
            self.__debugging = False

        def hijack(arb):
            str_in = args[1]
            in_codes = map(int, str_in.split(','))
            for offset, code in enumerate(in_codes):
                self.vm.memory.write(offset + 30100, code)
            self.vm.pointer = 30100

        commands = {'!dump': dump, '!start': start,
                    '!stop': stop, '!hijack': hijack}
        args = input_str.split(' ')

        if args[0] not in commands:
            print 'invalid command'
            return

        commands[args[0]](args)

    def print_current(self):
        pointer = self.vm.pointer

        current_op = self.vm.memory.read(pointer)

        [op_name, num_args] = self.op_names[current_op]

        args = [self.vm.memory.read(pointer + 1 + i) for i in
                xrange(num_args)]

        def call(args):
            callee = self.vm.resolve(args[0])
            name = self.__function_names.get(callee, '')
            return 'call %d %s' % (callee, name)

        style_op = {'call': call}

        print ' ' * len(self.__call_stack) + str(pointer) + ': ' + style_op[op_name](args)

    def is_debugging(self):
        return self.__debugging

    def step(self):
        if self.__debugging and self.vm.memory.read(self.vm.pointer) == 17:
            self.print_current()

        # update depth after display
        if self.vm.memory.read(self.vm.pointer) == 17:
            self.__call_stack.append(self.vm.memory.read(self.vm.pointer + 1))
        if self.vm.memory.read(self.vm.pointer) == 18:
            self.__call_stack.pop()


terminal = terminal()
in_fn = terminal.get_char
out_fn = terminal.print_char

emulator = vm(in_fn, out_fn)
debugger = debugger(emulator)

# terminal needs reference for access in cheatmode
terminal.debugger = debugger

emulator.load_binary("challenge.bin")

while True:
    emulator.step()
    debugger.step()
