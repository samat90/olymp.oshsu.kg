import sys

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    n, k = int(d[1 + 2 * t]), int(d[2 + 2 * t])
    people = list(range(1, n + 1))
    i = 0
    while len(people) > 1:
        i = (i + k - 1) % len(people)
        people.pop(i)
    out.append(people[0])
print('\n'.join(map(str, out)))
