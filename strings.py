with open('logs/boot.log', 'r') as f:
    contents = f.readlines()

contents = [int(line.strip().split(':')[1]) for line in contents[7:]]

words = []
current = ''
for i, code in enumerate(contents):
    if code > 256 or (code < 32 and code != 10):
        if current == '':
            continue
        words.append(current)
        current = ''
        continue
    character = chr(code)
    if character == '\n':
        character = '\\n'
    current += character

print '\n'.join(words)
