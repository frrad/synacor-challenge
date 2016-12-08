#!/usr/bin/python

start = int(raw_input("start address: "))

with open('logs/boot.log', 'r') as f:
    contents = f.readlines()
contents = [int(line.strip().split(':')[1]) for line in contents[7:]]

size = contents[start]
print 'size: ', size
data = contents[start + 1:start + size + 1]

keys = set()
valid_set = [10] + range(32, 128)
for j, datum in enumerate(data):
    these_keys = set([i ^ datum for i in valid_set])

    if j == 0:
        keys = these_keys
    keys &= these_keys


if len(keys) == len(valid_set) or len(keys) == 0:
    print 'fail'
else:
    for key in keys:
        decode = [datum ^ key for datum in data]
        print key
        print ''.join(map(chr, decode))

    if len(keys) != 1:
        answer = int(raw_input("answer please").strip())
    else:
        answer = list(keys)[0]
    print "%d:%d:%d" % (start + 1, start + size, answer)
