#!/usr/bin/python


with open('logs/boot.log', 'r') as f:
    contents = f.readlines()
contents = [int(line.strip().split(':')[1]) for line in contents[7:]]


def decode(start):
    size = contents[start]
    data = contents[start + 1:start + size + 1]

    keys = set()
    valid_set = [10] + range(32, 60) + range(61, 64) + \
        range(65, 96) + range(97, 123)
    for j, datum in enumerate(data):
        these_keys = set([i ^ datum for i in valid_set])

        if j == 0:
            keys = these_keys
        keys &= these_keys

    if len(keys) == len(valid_set) or len(keys) == 0:
        print 'fail'
        return False

    if len(keys) == 1:
        answer = list(keys)[0]
    elif 0 in keys:
        answer = 0
    else:
        for key in keys:
            decode = [datum ^ key for datum in data]
            print key
            print ''.join(map(chr, decode))

        answer = int(raw_input("answer please").strip())

    decode = [datum ^ answer for datum in data]
    # print ''.join(map(chr, decode)), answer

    return (start + 1, start + size, answer)


start = int(raw_input("start address: "))
answer = True
while answer:
    answer = decode(start)
    if answer:
        print "%d:%d:%d" % answer
        start = answer[1] + 1
