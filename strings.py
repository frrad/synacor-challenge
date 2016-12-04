with open('logs/boot.log', 'r') as f:
    contents = f.readlines()

contents = [int(line.strip().split(':')[1]) for line in contents[7:]]


current = ''
breaker = 3
for i, code in enumerate(contents):
    if code == 19:
        code = contents[i + 1]
        if code < 256:
            character = chr(code)
            if character == '\n':
                character = '\\n'
            current += character
            breaker += 1
    else:
        breaker -= 1

    if breaker == 0:
        breaker = 3
        if current != '':
            print current
            current = ''
