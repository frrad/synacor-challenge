#!/usr/bin/python

with open('logs/boot.log', 'r') as f:
    data = f.readlines()
data = [int(line.strip().split(':')[1]) for line in data[7:]]


def read_str(address):
    length = data[address]
    answer = ''
    for i in xrange(length):
        char_code = data[address + 1 + i]
        if char_code < 128:
            answer += chr(char_code)
    return answer


def read_vec(address):
    length = data[address]
    answer = []
    for i in xrange(length):
        answer.append(data[address + 1 + i])
    return answer


class room:

    def __init__(self, start, addr_keyed_collection):
        self.addr = start

        addr_keyed_collection[self.addr] = self

        name_ptr = data[start]
        self.name = read_str(name_ptr)
        desc_ptr = data[start + 1]
        self.description = read_str(desc_ptr)
        exit_vec_ptr = data[start + 2]
        self.exit_vec = map(read_str, read_vec(exit_vec_ptr))

        exit_dest_vec_ptr = data[start + 3]
        dest_addr_vec = read_vec(exit_dest_vec_ptr)
        self.dest_vec = []
        for dest_addr in dest_addr_vec:
            if dest_addr in addr_keyed_collection:
                self.dest_vec.append(addr_keyed_collection[dest_addr])
            else:
                child_room = room(dest_addr, addr_keyed_collection)
                self.dest_vec.append(child_room)

    def children_names(self):
        return zip(self.exit_vec, [room.name for room in self.dest_vec])

collection = dict()
foothills = room(2317, collection)

for addr in collection:
    room = collection[addr]
    print room.name, room.children_names()


# for addr in collection:
#     room = collection[addr]
#     print "%d:\"%s\"" % (addr, room.name)
