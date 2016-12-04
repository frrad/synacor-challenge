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

def add(memory, registers, pointer):
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


def out(memory, registers, pointer):
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


def noop(memory, registers, pointer):
    if memory.read(pointer) != 21:
        error("operation at %d not a noop" % pointer)

    debug("noop")
    pointer += 1
    return pointer


ops = {9: add, 19: out, 21: noop}

# end op definitions


# initialize
mem = memory()
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
    pointer = op(mem, registers, pointer)
