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

    def var_unique_name(self):
        return self.unique_name.replace(' ', '_').replace('"', '').replace('!', '').lower()

    def __init__(self, start, addr_keyed_collection, name_set):
        self.addr = start

        addr_keyed_collection[self.addr] = self

        name_ptr = data[start]
        self.name = read_str(name_ptr)

        base_unique_name = '"%s"' % self.name
        if base_unique_name not in name_set:
            self.unique_name = base_unique_name
            name_set.add(self.unique_name)
        else:
            name = base_unique_name
            j = 1
            while name in name_set:
                j += 1
                name = base_unique_name + " " + str(j)
            self.unique_name = name
            name_set.add(name)

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
                child_room = room(dest_addr, addr_keyed_collection, name_set)
                self.dest_vec.append(child_room)

        self.fn_ptr = data[start + 4]

    def children_names(self):
        return zip(self.exit_vec, [room.name for room in self.dest_vec])

collection = dict()
name_set = set()

for addr in range(2322, 2462, 5) + range(2463, 2666, 5):
    if addr in collection:
        continue
    room(addr, collection, name_set)


# for code annotation
# for addr in sorted(collection.keys()):
#     room = collection[addr]
#     print "%d:%s" % (addr, room.unique_name)
#     print "%d:%s" % (addr + 1, room.description[:30] + '...')

#     if room.fn_ptr > 0:
#         print "%d:enter_%s" % (room.fn_ptr, room.var_unique_name())


formatted_names = []
arrows = []
for addr in sorted(collection.keys()):
    room = collection[addr]
    room_name = room.var_unique_name()
    formatted_names.append(room_name)

    for exit_name, child_room in zip(room.exit_vec, room.dest_vec):
        child_room_name = child_room.var_unique_name()
        arrows.append('%s -> %s[label = "%s"]' %
                      (room_name, child_room_name, exit_name))

print "digraph map {"
print "  rankdir=LR;"
print "  size=\"50,50\""
print '  node [shape = circle, fontsize = 25]; %s;' % ' '.join(formatted_names)
print '  edge [ fontsize = 30];'
for arrow in arrows:
    print'  ', arrow
print '}'
