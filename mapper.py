#!/usr/bin/python


with open('logs/boot.log', 'r') as f:
    data = f.readlines()
data = [int(line.strip().split(':')[1]) for line in data[7:]]


def read_val(address):
    return data[address]


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
        answer = self.unique_name.replace(' ', '_')
        return answer.replace('"', '').replace('!', '').lower()

    def __init__(self, start, addr_keyed_collection, name_set):
        self.item_set = set()

        self.addr = start

        addr_keyed_collection[self.addr] = self

        name_ptr = data[self.addr]
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

        desc_ptr = data[self.addr + 1]
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


class item:
    all_items = set()

    def var_name(self):
        answer = self.name.replace(' ', '_')
        return answer.replace('"', '').replace('!', '').lower()

    def __init__(self, pointer, room_collection):
        item.all_items.add(self)

        self.addr = pointer

        name_ptr = read_val(pointer)
        self.name = read_str(name_ptr)

        desc_ptr = read_val(pointer + 1)
        self.description = read_str(desc_ptr)

        room_ptr = read_val(pointer + 2)
        self.has_room = False
        if room_ptr < 32767:  # -1 is "unset"
            self.has_room = True
            room_collection[room_ptr].item_set.add(self)
            self.room = room_collection[room_ptr]

        self.fn_ptr = read_val(pointer + 3)


collection = dict()
name_set = set()

for addr in range(2322, 2462, 5) + range(2463, 2666, 5):
    if addr in collection:
        continue
    room(addr, collection, name_set)


for pointer in read_vec(27381):
    item(pointer, collection)


def print_code_notes():
    fn_lines = []
    note_lines = []

    fn_lines += ['# enter room functions']
    note_lines += ['# room notes']
    for addr in sorted(collection.keys()):
        room = collection[addr]
        note_lines.append("%d:%s" % (addr, room.unique_name))
        note_lines.append("%d:%s" % (addr + 1, room.description[:30] + '...'))
        if room.fn_ptr > 0:
            fn_lines.append("%d:enter_%s" %
                            (room.fn_ptr, room.var_unique_name()))

    fn_lines += ['# use object functions']
    note_lines += ['# object notes']
    for thing in item.all_items:
        note_lines.append("%d:\"%s\"" % (thing.addr, thing.name))
        note_lines.append("%d:%s" %
                          (thing.addr + 1, thing.description[:30] + "..."))
        if thing.has_room:
            note_lines.append("%d:room=%s" %
                              (thing.addr + 2, thing.room.unique_name))

        if thing.fn_ptr:
            fn_lines.append("%d:use_%s" % (thing.fn_ptr, thing.var_name()))

    print '\n'
    print '\n'.join(note_lines)
    print '\n'
    print '\n'.join(fn_lines)


def print_graphviz():
    formatted_names_no_items = []
    formatted_names_items = []
    arrows = []
    for addr in sorted(collection.keys()):
        room = collection[addr]
        room_name = room.var_unique_name()
        if len(room.item_set) == 0:
            formatted_names_no_items.append(room_name)
        else:
            node = room_name

            thing_list = ''
            for thing in room.item_set:
                thing_list += '\n' + thing.name

            node += "[label=\"%s\"]" % (room_name + ':' + thing_list)

            formatted_names_items.append(node)

        for exit_name, child_room in zip(room.exit_vec, room.dest_vec):
            child_room_name = child_room.var_unique_name()
            arrows.append('%s -> %s[label = "%s"]' %
                          (room_name, child_room_name, exit_name))

    print "digraph map {"
    print "  rankdir=UD;"
    print "  size=\"50,50\""
    print '  node [shape = ellipse, fontsize = 25]; %s;' % ' '.join(formatted_names_no_items)
    print '  node [shape = rectangle, fontsize = 25]; %s;' % ' '.join(formatted_names_items)
    print '  edge [ fontsize = 30];'
    for arrow in arrows:
        print'  ', arrow
    print '  edge [ fontsize = 30, style = dashed];'
    print '  passage_2 -> fumbling_around_in_the_darkness[label = "continue"]'
    print '  twisty_passages_9 -> twisty_passages_10'
    print '}'

print_graphviz()
# print_code_notes()
