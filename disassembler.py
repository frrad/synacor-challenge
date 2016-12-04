with open('logs/boot.log', 'r') as f:
    contents = f.readlines()

contents = [int(line.strip().split(':')[1]) for line in contents[7:]]


def disp(arg):
    if arg[0] > 256:
        return
    out = chr(arg[0])
    if out == '\n':
        out = '\\n'
    print out,

opcodes = {0: ['halt', 0],
           1: ['set', 2],
           2: ['push', 1],
           3: ['pop', 1],
           4: ['eq', 3],
           5: ['gt', 3],
           6: ['jmp', 1],
           7: ['jt', 2],
           8: ['jf', 2],
           9: ['add', 3],
           10: ['add', 3],
           11: ['mod', 3],
           12: ['and', 3],
           13: ['or', 3],
           14: ['not', 2],
           15: ['rmem', 2],
           16: ['wmem', 2],
           17: ['call', 1],
           18: ['ret', 0],
           19: ['out', 1, disp],
           20: ['in', 1],
           21: ['noop', 0]}

i = 0
while i < len(contents):
    here = contents[i]
    print i, "\t:",

    if here < 22:
        op = opcodes[here]
        print op[0],
        args = []
        for j in xrange(op[1]):
            i += 1
            args.append(contents[i])
        print args, '\t\t\t',
        if len(op) > 2:
            op[2](args)
    else:
        print here,

    print ''

    i += 1
