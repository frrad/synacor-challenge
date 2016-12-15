mod = 2 ** 15


def calibrate_teleporter(x, y, answer):  # // function:calibrate_teleporter
    x %= mod
    y %= mod

    #    print x, y
    if (x, y) in memo:
        return memo[(x, y)]

    if x == 0:
        return (y + 1) % mod

    if y == 0:
        ans = calibrate_teleporter(x - 1, answer, answer) % mod
        memo[(x, y)] = ans
        return ans

    ans = calibrate_teleporter(
        x - 1,  calibrate_teleporter(x, y - 1, answer), answer) % mod
    memo[(x, y)] = ans
    return ans


memo = dict()

answer = 25734

for x in xrange(4):
    for y in xrange(2**15):
        calibrate_teleporter(x, y, answer)


print answer, calibrate_teleporter(4, 1, 25734)
