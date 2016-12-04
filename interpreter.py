def debug(message):
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
                    ''.join(reversed(byte)).encode('hex'), 16))
                address += 1
                byte = f.read(2)

    def write(self, address, value):
        if address >= self.__address_space:
            debug("address out of bounds %d > %d" %
                  (address, self.__address_space))
            return
        if value >= self.__value_size:
            debug("value out of bounds %d > %d" %
                  (value, self.__address_space))
            return
        self.__memory[address] = value

    def read(self, address):
        if address >= self.__address_space:
            debug("address out of bounds %d > %d" %
                  (address, self.__address_space))
            return
        return self.__memory[address]

    def test(self):
        print self.__memory[1:100]

mem = memory()
mem.load_file("challenge.bin")
mem.test()
