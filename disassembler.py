#!/usr/bin/python


import sys

with open('logs/boot.log', 'r') as f:
    contents = f.readlines()
contents = [int(line.strip().split(':')[1]) for line in contents[7:]]


var_names = {}
notes = {}
decode_lines = {}
data_lines = set()
function_names = {}

with open('notes/notes.txt', 'r') as f:
    for line in f:
        if len(line) == 0 or line[0] == '#' or line == '\n':
            continue
        a = line.strip().split(':')
        notes[int(a[0])] = a[1]


with open('notes/text.txt', 'r') as f:
    for line in f:
        if len(line) == 0 or line[0] == '#' or line == '\n':
            continue
        a = [int(j) for j in line.strip().split(':')]

        line_before = a[0] - 1
        data_lines.add(line_before)
        if a[2] != 0:
            notes[line_before] = notes.get(
                line_before, "") + "string XOR with %d" % int(a[2])
        else:
            notes[line_before] = notes.get(
                line_before, "") + "start string"

        for i in xrange(a[0], a[1] + 1):
            decode_lines[i] = int(a[2])


with open('notes/data.txt', 'r') as f:
    for line in f:
        if len(line) == 0 or line[0] == '#' or line == '\n':
            continue
        a = [int(j) for j in line.strip().split(':')]

        if len(a) == 2:
            for i in xrange(a[0], a[1] + 1):
                data_lines.add(i)
        if len(a) == 1:
            data_lines.add(a[0])


with open('notes/functions.txt', 'r') as f:
    for line in f:
        if len(line) == 0 or line[0] == '#' or line == '\n':
            continue
        a = line.strip().split(':')
        function_names[int(a[0])] = a[1]


with open('notes/vars.txt', 'r') as f:
    for line in f:
        if len(line) == 0 or line[0] == '#' or line == '\n':
            continue
        a = line.strip().split(':')
        min_line = int(a[0])
        max_line = int(a[1])
        reg = int(a[2])
        name = a[3]
        for x in xrange(min_line, max_line + 1):
            if x not in var_names:
                var_names[x] = {}
            var_names[x][reg] = name

for i in function_names:
    notes[i] = 'function: ' + function_names[i] + ' ' + notes.get(i, '')


# end prep

def disp_out(arg, emit):
    if arg[0] > 256:
        return emit
    out = chr(arg[0])
    if out == '\n':
        out = '\\n'
    return emit + '    ' + out


def disp_call(arg, emit):
    address = arg[0]
    if address in function_names:
        return emit + '    ' + function_names[address]
    return emit


def decode_registers(arg, i):
    if arg >= 32768 and arg <= 32775:
        reg = arg - 32768
        if i in var_names and reg in var_names[i]:
            return '(%s:%d)' % (var_names[i][reg], reg)

        return '(reg:' + str(reg) + ")"
    return str(arg)

opcodes = {0: ['halt', 0],
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
           17: ['call', 1, disp_call],
           18: ['ret ', 0],
           19: ['out ', 1, disp_out],
           20: ['in  ', 1],
           21: ['noop', 0]}


i = 0
while i < len(contents) and i < 30050:
    beginning_i = i

    to_print = ''
    here = contents[i]

    if i in decode_lines and (here ^ decode_lines[i]) < 128:
        sys.stdout.write(chr(here ^ decode_lines[i]))
        i += 1
        continue

    if i in decode_lines:
        print 'ERROR:', i
        sys.exit(i)
    if i - 1 in decode_lines:
        to_print += '\n'

    to_print += "%-6s" % (str(i) + ':')

    if here < 22 and i not in data_lines:
        op = opcodes[here]
        to_print += op[0]
        args = []
        for j in xrange(op[1]):
            i += 1
            args.append(contents[i])
        names = [decode_registers(arg, i + k - op[1] + 1)
                 for k, arg in enumerate(args)]
        to_print += "%40s" % ' '.join(names)
        if len(op) > 2:
            to_print = op[2](args, to_print)
    else:
        to_print += "%-40d" % here

    suffix = ''
    if beginning_i in notes:
        suffix = '// ' + notes[beginning_i]
    to_print = to_print + '    ' + suffix
    sys.stdout.write(to_print.rstrip(' ') + '\n')

    i += 1
