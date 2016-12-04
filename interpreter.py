import sys

modulus = 32768


def terminal_out(character):
    sys.stdout.write(character)


def error(message):
    sys.exit("ERROR: " + message)


def debug(message, level=1):
    debug_level = 2

    if level >= debug_level:
        print message


class stack:

    def __init__(self):
        self.__stack = list()

    def push(self, value):
        self.__stack.append(value)

    def pop(self):
        return self.__stack.pop()


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
        debug("begin loading list")
        for address, value in enumerate(input):
            self.write(address, value, level=-1)
        debug("list loaded")

    def write(self, address, value, level=0):
        if address >= self.__address_space:
            error("address out of bounds %d > %d" %
                  (address, self.__address_space))
            return
        if value >= self.__value_size:
            error("value out of bounds %d > %d" %
                  (value, self.__address_space))
            return

        debug("writing %d to memory address %d" %
              (value, address), 1 + level)
        self.__memory[address] = value

    def read(self, address):
        if address >= self.__address_space:
            error("address out of bounds %d > %d" %
                  (address, self.__address_space))
            return
        return self.__memory[address]

    def inspect(self, start, end):
        debug(self.__memory[start:end])


def resolve(value, registers):
    max_literal = 32767
    num_registers = 8

    if value < 0 or value > max_literal + num_registers:
        error("cannot resolve value %d" % value)
    if value <= max_literal:
        debug("resolved value %d: literal" % value)
        return value

    register = value - max_literal - 1
    new_value = registers[register]

    debug("resolved value %d: register %d = %d" %
          (value, register, new_value))
    return new_value


def store(address, value, registers, memory):
    max_address = 32767
    num_registers = 8

    if address <= max_address:
        memory.write(address, value)
        return

    register_number = address - max_address - 1
    if register_number >= num_registers:
        error("trying to write to invalid register %d" % register_number)
        return

    debug("writing %d to register %d" % (value, register_number))
    registers[register_number] = value


# begin op definitions

def halt(memory, registers, pointer, stack):
    if memory.read(pointer) != 0:
        error("operation at %d not a halt" % pointer)
    """halt: 0
    stop execution and terminate the program
    """
    debug("halting")
    sys.exit()


def set_op(memory, registers, pointer, stack):
    """set: 1 a b
    set register <a> to the value of <b>
    """
    if memory.read(pointer) != 1:
        error("operation at %d not a set" % pointer)

    pointer += 1
    destination = memory.read(pointer)
    pointer += 1
    value = resolve(memory.read(pointer), registers)
    pointer += 1

    debug("storing %d in %d" % (value, destination))
    store(destination, value, registers, memory)

    return pointer


def push(memory, registers, pointer, stack):
    """push: 2 a
    push <a> onto the stack
    """
    if memory.read(pointer) != 2:
        error("operation at %d not a push" % pointer)

    pointer += 1
    value = resolve(memory.read(pointer), registers)
    pointer += 1

    stack.push(value)

    return pointer


def pop(memory, registers, pointer, stack):
    """pop: 3 a
    remove the top element from the stack and write it into <a>; empty stack
    = error
    """
    if memory.read(pointer) != 3:
        error("operation at %d not a pop" % pointer)

    pointer += 1
    destination = memory.read(pointer)
    pointer += 1

    store(destination, stack.pop(), registers, memory)

    return pointer


def eq(memory, registers, pointer, stack):
    """eq: 4 a b c
    set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
    """
    if memory.read(pointer) != 4:
        error("operation at %d not an eq" % pointer)

    pointer += 1
    output = memory.read(pointer)
    pointer += 1
    lhs = resolve(memory.read(pointer), registers)
    pointer += 1
    rhs = resolve(memory.read(pointer), registers)
    pointer += 1

    if lhs == rhs:
        store(output, 1, registers, memory)
    else:
        store(output, 0, registers, memory)

    return pointer


def gt(memory, registers, pointer, stack):
    """gt: 5 a b c
    set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
    """
    if memory.read(pointer) != 5:
        error("operation at %d not a gt" % pointer)

    pointer += 1
    output = memory.read(pointer)
    pointer += 1
    lhs = resolve(memory.read(pointer), registers)
    pointer += 1
    rhs = resolve(memory.read(pointer), registers)
    pointer += 1

    if lhs > rhs:
        store(output, 1, registers, memory)
    else:
        store(output, 0, registers, memory)

    return pointer


def jmp(memory, registers, pointer, stack):
    """jmp: 6 a
    jump to <a>
    """
    if memory.read(pointer) != 6:
        error("operation at %d not a jmp" % pointer)

    pointer += 1
    destination = resolve(memory.read(pointer), registers)
    pointer += 1

    return destination


def jt(memory, registers, pointer, stack):
    """jt: 7 a b
    if <a> is nonzero, jump to <b>
    """
    if memory.read(pointer) != 7:
        error("operation at %d not a jt" % pointer)

    pointer += 1
    test = resolve(memory.read(pointer), registers)
    pointer += 1
    destination = resolve(memory.read(pointer), registers)
    pointer += 1

    if test != 0:
        return destination

    return pointer


def jf(memory, registers, pointer, stack):
    """jf: 8 a b
    if <a> is zero, jump to <b>
    """
    if memory.read(pointer) != 8:
        error("operation at %d not a jf" % pointer)

    pointer += 1
    test = resolve(memory.read(pointer), registers)
    pointer += 1
    destination = resolve(memory.read(pointer), registers)
    pointer += 1

    if test == 0:
        return destination

    return pointer


def add(memory, registers, pointer, stack):
    ''' add: 9 a b c
   assign into <a> the sum of <b> and <c> (modulo 32768)'''

    if memory.read(pointer) != 9:
        error("operation at %d not an add" % pointer)
    pointer += 1
    destination = memory.read(pointer)
    pointer += 1
    summand_1 = memory.read(pointer)
    pointer += 1
    summand_2 = memory.read(pointer)
    pointer += 1

    summand_1 = resolve(summand_1, registers)
    summand_2 = resolve(summand_2, registers)

    total = (summand_1 + summand_2) % modulus

    debug("add: %d + %d = %d (storing in %d)" %
          (summand_1, summand_2, total, destination))
    store(destination, total, registers, memory)

    return pointer


def mult(memory, registers, pointer, stack):
    """mult: 10 a b c
    store into <a> the product of <b> and <c> (modulo 32768)
    """
    if memory.read(pointer) != 10:
        error("operation at %d not a mult" % pointer)
    pointer += 1
    destination = memory.read(pointer)
    pointer += 1
    multiplicand_1 = resolve(memory.read(pointer), registers)
    pointer += 1
    multiplicand_2 = resolve(memory.read(pointer), registers)
    pointer += 1

    total = (multiplicand_1 * multiplicand_2) % modulus

    debug("mult: %d * %d = %d (storing in %d)" %
          (multiplicand_1, multiplicand_2, total, destination))
    store(destination, total, registers, memory)

    return pointer


def mod(memory, registers, pointer, stack):
    """mod: 11 a b c
    store into <a> the remainder of <b> divided by <c>
    """
    if memory.read(pointer) != 11:
        error("operation at %d not a mod" % pointer)
    pointer += 1
    destination = memory.read(pointer)
    pointer += 1
    dividend = resolve(memory.read(pointer), registers)
    pointer += 1
    divisor = resolve(memory.read(pointer), registers)
    pointer += 1

    result = dividend % divisor

    debug("mod: %d mod %d = %d (storing in %d)" %
          (dividend, divisor, result, destination))
    store(destination, result, registers, memory)

    return pointer


def and_op(memory, registers, pointer, stack):
    """and: 12 a b c
    stores into <a> the bitwise and of <b> and <c>
    """
    if memory.read(pointer) != 12:
        error("operation at %d not a and" % pointer)

    pointer += 1
    output = memory.read(pointer)
    pointer += 1
    lhs = resolve(memory.read(pointer), registers)
    pointer += 1
    rhs = resolve(memory.read(pointer), registers)
    pointer += 1

    result = lhs & rhs

    debug("bitwise and of %d and %d is %d" % (lhs, rhs, result))

    store(output, result, registers, memory)

    return pointer


def or_op(memory, registers, pointer, stack):
    """or: 13 a b c
    stores into <a> the bitwise or of <b> and <c>
    """
    if memory.read(pointer) != 13:
        error("operation at %d not an or" % pointer)

    pointer += 1
    output = memory.read(pointer)
    pointer += 1
    lhs = resolve(memory.read(pointer), registers)
    pointer += 1
    rhs = resolve(memory.read(pointer), registers)
    pointer += 1

    result = lhs | rhs

    debug("bitwise or of %d and %d is %d" % (lhs, rhs, result))

    store(output, result, registers, memory)

    return pointer


def not_op(memory, registers, pointer, stack):
    """not: 14 a b
    stores 15-bit bitwise inverse of <b> in <a>
    """
    if memory.read(pointer) != 14:
        error("operation at %d not a not" % pointer)

    pointer += 1
    output = memory.read(pointer)
    pointer += 1
    to_invert = resolve(memory.read(pointer), registers)
    pointer += 1

    result = to_invert ^ (2**15 - 1)

    debug("bitwise inverse of %d is %d" % (to_invert, result))

    store(output, result, registers, memory)

    return pointer


def rmem(memory, registers, pointer, stack):
    """rmem: 15 a b
    read memory at address <b> and write it to <a>
    """
    if memory.read(pointer) != 15:
        error("operation at %d not an rmem" % pointer)

    pointer += 1
    output = memory.read(pointer)
    pointer += 1
    source = resolve(memory.read(pointer), registers)
    pointer += 1

    result = memory.read(source)

    debug("writing %d to %d" % (result, output))
    store(output, result, registers, memory)

    return pointer


def wmem(memory, registers, pointer, stack):
    """wmem: 16 a b
    write the value from <b> into memory at address <a>
    """
    if memory.read(pointer) != 16:
        error("operation at %d not a wmem" % pointer)

    pointer += 1
    address = resolve(memory.read(pointer), registers)
    pointer += 1
    value = resolve(memory.read(pointer), registers)
    pointer += 1

    debug("writing %d to %d" % (value, address))
    memory.write(address, value)

    return pointer


def call(memory, registers, pointer, stack):
    """call: 17 a
    write the address of the next instruction to the stack and jump to <a>
    """
    if memory.read(pointer) != 17:
        error("operation at %d not a call" % pointer)

    pointer += 1
    output = resolve(memory.read(pointer), registers)
    pointer += 1

    debug("writing %d to stack, jumping to %d" % (pointer, output))
    stack.push(pointer)

    return output


def ret(memory, registers, pointer, stack):
    """ret: 18
    remove the top element from the stack and jump to it; empty stack = halt
    """
    if memory.read(pointer) != 18:
        error("operation at %d not a ret" % pointer)

    dest = stack.pop()

    debug("returning to %d" % dest)

    return dest


def out(memory, registers, pointer, stack):
    """ out: 19 a
    write the character represented by ascii code <a> to the terminal
    """
    if memory.read(pointer) != 19:
        error("operation at %d not an out" % pointer)
    pointer += 1
    character_code = memory.read(pointer)
    pointer += 1

    character_code = resolve(character_code, registers)
    character = chr(character_code)

    debug("writing character %s (%d) to terminal" %
          (character, character_code))
    terminal_out(character)

    return pointer


# in: 20 a
# read a character from the terminal and write its ascii code to <a>; it
# can be assumed that once input starts, it will continue until a newline
# is encountered; this means that you can safely read whole lines from the
# keyboard and trust that they will be fully read


def noop(memory, registers, pointer, stack):
    """noop: 21
      no operation
    """
    if memory.read(pointer) != 21:
        error("operation at %d not a noop" % pointer)

    debug("noop")
    pointer += 1
    return pointer


ops = {0: halt, 1: set_op, 2: push, 3: pop, 4: eq, 5: gt, 6: jmp,
       7: jt, 8: jf,  9: add, 10: mult, 11: mod, 12: and_op, 13: or_op, 14: not_op, 15: rmem, 16: wmem, 17: call, 18: ret, 19: out, 21: noop}

# end op definitions


# initialize
mem = memory()
stack = stack()
registers = [0] * 8
pointer = 0

# load program
mem.load_file("challenge.bin")
# mem.load_list([9, 32768, 32769, 4, 19, 32768])


while True:
    opcode = mem.read(pointer)
    if opcode not in ops:
        error("opcode %d not in opcode table" % opcode)
    op = ops[opcode]
    pointer = op(mem, registers, pointer, stack)
