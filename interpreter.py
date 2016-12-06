#!/usr/bin/python

import sys


def error(message):
    sys.exit("ERROR: " + message)


class stack:

    def __init__(self):
        self.__stack = list()

    def push(self, value):
        self.__stack.append(value)

    def pop(self):
        return self.__stack.pop()

    def debug(self):
        return str(self.__stack)


class memory:
    """Memory. Values are ints."""

    def __init__(self):
        self.__address_space = 2**15
        self.__value_size = 2**16
        self.__memory = [0] * self.__address_space

    def load_file(self, path):
        address = 0
        with open(path, "rb") as f:
            byte = f.read(2)
            while byte != "":
                self.write(address,  int(
                    ''.join(reversed(byte)).encode('hex'), 16), -1)
                address += 1
                byte = f.read(2)

    def load_list(self, input):
        for address, value in enumerate(input):
            self.write(address, value, level=-1)

    def write(self, address, value, level=0):
        if address >= self.__address_space:
            error("address out of bounds %d > %d" %
                  (address, self.__address_space))
            return
        if value >= self.__value_size:
            error("value out of bounds %d > %d" %
                  (value, self.__address_space))
            return

        self.__memory[address] = value

    def read(self, address):
        if address >= self.__address_space:
            error("address out of bounds %d > %d" %
                  (address, self.__address_space))
            return
        return self.__memory[address]

    def inspect(self, start, end):
        return self.__memory[start:end + 1]


class vm:

    def __init__(self, in_fn, out_fn):
        self.out_fn = out_fn
        self.in_fn = in_fn

        self.__modulus = 2**15
        self.__max_literal = self.__modulus - 1
        self.__num_registers = 8

        self.memory = memory()
        self.stack = stack()
        self.registers = [0] * self.__num_registers
        self.pointer = 0

        self.__ops = {0: self.__HALT, 1: self.__SET, 2: self.__PUSH,
                      3: self.__POP, 4: self.__EQ, 5: self.__GT,
                      6: self.__JMP, 7: self.__JT, 8: self.__JF,
                      9: self.__ADD, 10: self.__MULT, 11: self.__MOD,
                      12: self.__AND, 13: self.__OR, 14: self.__NOT,
                      15: self.__RMEM, 16: self.__WMEM, 17: self.__CALL,
                      18: self.__RET, 19: self.__OUT, 20: self.__IN,
                      21: self.__NOOP}

    def dump_state(self, filename):
        with open(filename, 'w') as f:
            f.write('registers\n')
            f.write(str(self.registers))
            f.write('\npointer\n')
            f.write(str(self.pointer))
            f.write('\nstack\n')
            f.write(self.stack.debug())
            f.write('\nmemory\n')
            for address in xrange(2**15):
                f.write(str(address) + ':')
                f.write(str(self.memory.read(address)))
                f.write('\n')

    def step(self):
        opcode = self.memory.read(self.pointer)
        if opcode not in self.__ops:
            error("opcode %d not in opcode table" % opcode)
        op = self.__ops[opcode]
        op()

    def load_binary(self, path):
        self.memory.load_file(path)

    # op helper functions
    def resolve(self, value):
        registers = self.registers

        if value < 0 or value > self.__max_literal + self.__num_registers:
            error("cannot resolve value %d" % value)
        if value <= self.__max_literal:

            return value

        register = value - self.__max_literal - 1
        new_value = self.registers[register]

        return new_value

    def set_register(self, destination, value):
        if destination <= self.__max_literal:
            error("try to set non-register")

        register_number = destination - self.__max_literal - 1
        if register_number >= self.__num_registers:
            error("trying to write to invalid register %d" % register_number)

        self.registers[register_number] = value

    # begin op definitions
    def __HALT(self):
        """halt: 0
        stop execution and terminate the program
        """
        if self.memory.read(self.pointer) != 0:
            error("operation at %d not a halt" % self.pointer)

        sys.exit()

    def __SET(self):
        """set: 1 a b
        set register <a> to the value of <b>
        """
        if self.memory.read(self.pointer) != 1:
            error("operation at %d not a set" % pointer)

        self.pointer += 1
        destination = self.memory.read(self.pointer)
        self.pointer += 1
        value = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        self.set_register(destination, value)

    def __PUSH(self):
        """push: 2 a
        push <a> onto the stack
        """
        if self.memory.read(self.pointer) != 2:
            error("operation at %d not a push" % pointer)

        self.pointer += 1
        value = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        self.stack.push(value)

    def __POP(self):
        """pop: 3 a
        remove the top element from the stack and write it into <a>; empty stack
        = error
        """
        if self.memory.read(self.pointer) != 3:
            error("operation at %d not a pop" % pointer)

        self.pointer += 1
        destination = self.memory.read(self.pointer)
        self.pointer += 1

        self.set_register(destination, self.stack.pop())

    def __EQ(self):
        """eq: 4 a b c
        set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
        """
        if self.memory.read(self.pointer) != 4:
            error("operation at %d not an eq" % pointer)

        self.pointer += 1
        output = self.memory.read(self.pointer)
        self.pointer += 1
        lhs = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        rhs = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        if lhs == rhs:
            self.set_register(output, 1)
        else:
            self.set_register(output, 0)

    def __GT(self):
        """gt: 5 a b c
        set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
        """
        if self.memory.read(self.pointer) != 5:
            error("operation at %d not a gt" % pointer)

        self.pointer += 1
        output = self.memory.read(self.pointer)
        self.pointer += 1
        lhs = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        rhs = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        if lhs > rhs:
            self.set_register(output, 1)
        else:
            self.set_register(output, 0)

    def __JMP(self):
        """jmp: 6 a
        jump to <a>
        """
        if self.memory.read(self.pointer) != 6:
            error("operation at %d not a jmp" % self.pointer)

        self.pointer += 1
        destination = self.resolve(self.memory.read(self.pointer))
        self.pointer = destination

    def __JT(self):
        """jt: 7 a b
        if <a> is nonzero, jump to <b>
        """
        if self.memory.read(self.pointer) != 7:
            error("operation at %d not a jt" % pointer)

        self.pointer += 1
        test = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        destination = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        if test != 0:
            self.pointer = destination

    def __JF(self):
        """jf: 8 a b
        if <a> is zero, jump to <b>
        """
        if self.memory.read(self.pointer) != 8:
            error("operation at %d not a jf" % self.pointer)

        self.pointer += 1
        test = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        destination = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        if test == 0:
            self.pointer = destination

    def __ADD(self):
        ''' add: 9 a b c
       assign into <a> the sum of <b> and <c> (modulo 32768)'''

        if self.memory.read(self.pointer) != 9:
            error("operation at %d not an add" % self.pointer)
        self.pointer += 1
        destination = self.memory.read(self.pointer)
        self.pointer += 1
        summand_1 = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        summand_2 = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        total = (summand_1 + summand_2) % self.__modulus

        self.set_register(destination, total)

    def __MULT(self):
        """mult: 10 a b c
        store into <a> the product of <b> and <c> (modulo 32768)
        """
        if self.memory.read(self.pointer) != 10:
            error("operation at %d not a mult" % pointer)
        self.pointer += 1
        destination = self.memory.read(self.pointer)
        self.pointer += 1
        multiplicand_1 = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        multiplicand_2 = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        total = (multiplicand_1 * multiplicand_2) % self.__modulus

        self.set_register(destination, total)

    def __MOD(self):
        """mod: 11 a b c
        store into <a> the remainder of <b> divided by <c>
        """
        if self.memory.read(self.pointer) != 11:
            error("operation at %d not a mod" % pointer)
        self.pointer += 1
        destination = self.memory.read(self.pointer)
        self.pointer += 1
        dividend = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        divisor = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        result = dividend % divisor

        self.set_register(destination, result)

    def __AND(self):
        """and: 12 a b c
        stores into <a> the bitwise and of <b> and <c>
        """
        if self.memory.read(self.pointer) != 12:
            error("operation at %d not a and" % pointer)

        self.pointer += 1
        output = self.memory.read(self.pointer)
        self.pointer += 1
        lhs = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        rhs = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        result = lhs & rhs

        self.set_register(output, result)

    def __OR(self):
        """or: 13 a b c
        stores into <a> the bitwise or of <b> and <c>
        """
        if self.memory.read(self.pointer) != 13:
            error("operation at %d not an or" % pointer)

        self.pointer += 1
        output = self.memory.read(self.pointer)
        self.pointer += 1
        lhs = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        rhs = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        result = lhs | rhs

        self.set_register(output, result)

    def __NOT(self):
        """not: 14 a b
        stores 15-bit bitwise inverse of <b> in <a>
        """
        if self.memory.read(self.pointer) != 14:
            error("operation at %d not a not" % pointer)

        self.pointer += 1
        output = self.memory.read(self.pointer)
        self.pointer += 1
        to_invert = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        result = to_invert ^ (2**15 - 1)

        self.set_register(output, result)

    def __RMEM(self):
        """rmem: 15 a b
        read memory at address <b> and write it to <a>
        """
        if self.memory.read(self.pointer) != 15:
            error("operation at %d not an rmem" % pointer)

        self.pointer += 1
        output = self.memory.read(self.pointer)
        self.pointer += 1
        source = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        result = self.memory.read(source)

        self.set_register(output, result)

    def __WMEM(self):
        """wmem: 16 a b
        write the value from <b> into memory at address <a>
        """
        if self.memory.read(self.pointer) != 16:
            error("operation at %d not a wmem" % pointer)

        self.pointer += 1
        address = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1
        value = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        self.memory.write(address, value, -1)

    def __CALL(self):
        """call: 17 a
        write the address of the next instruction to the stack and jump to <a>
        """
        if self.memory.read(self.pointer) != 17:
            error("operation at %d not a call" % pointer)

        self.pointer += 1
        output = self.resolve(self.memory.read(self.pointer))
        self.pointer += 1

        self.stack.push(self.pointer)

        self.pointer = output

    def __RET(self):
        """ret: 18
        remove the top element from the stack and jump to it; empty stack = halt
        """
        if self.memory.read(self.pointer) != 18:
            error("operation at %d not a ret" % pointer)

        dest = self.stack.pop()

        self.pointer = dest

    def __OUT(self):
        """ out: 19 a
        write the character represented by ascii code <a> to the terminal
        """
        if self.memory.read(self.pointer) != 19:
            error("operation at %d not an out" % pointer)
        self.pointer += 1
        character_code = self.memory.read(self.pointer)
        self.pointer += 1

        character_code = self.resolve(character_code)
        character = chr(character_code)

        self.out_fn(character)

    def __IN(self):
        """in: 20 a
        read a character from the terminal and write its ascii code to <a>; it
        can be assumed that once input starts, it will continue until a newline
        is encountered; this means that you can safely read whole lines from the
        keyboard and trust that they will be fully read
        """
        if self.memory.read(self.pointer) != 20:
            error("operation at %d not an in" % pointer)
        self.pointer += 1
        dest = self.memory.read(self.pointer)
        self.pointer += 1

        input = self.in_fn()
        input_ascii = ord(input)

        self.set_register(dest, input_ascii)

    def __NOOP(self):
        """noop: 21
          no operation
        """
        if self.memory.read(self.pointer) != 21:
            error("operation at %d not a noop" % pointer)

        self.pointer += 1
