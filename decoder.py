#!/usr/bin/python

start = int(raw_input("what start address"))

with open('logs/boot.log', 'r') as f:
    contents = f.readlines()
contents = [int(line.strip().split(':')[1]) for line in contents[7:]]

size = contents[start]

print 'size ', size

data = contents[start + 1:start + size + 1]


table = dict()
for datum in data:
    table[datum] = table.get(datum, 0) + 1

print sorted(table, key=lambda k: table[k])


for key in table:
    print key ^ 32
    print ''.join([chr(datum ^ (key ^ 32)) for datum in data])

answer = int(raw_input("answer please").strip())

print "%d:%d:%d" % (start + 1, start + size, answer)
