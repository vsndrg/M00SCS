import math
import random
import os

def write_tests(filename, cases):
    with open(filename, 'w', encoding='utf-8') as f:
        for inp, out in cases:
            f.write("####### TEST CASE #######\n")
            f.write(inp.rstrip() + "\n")
            f.write("---\n")
            f.write(str(out).rstrip() + "\n")
    print(f"Generated {len(cases)} cases in '{filename}'")

def gen_H01POW23():
    cases = []
    for n in [0, 1, -1]:
        cases.append((f"{n}", f"{n} * {n} = {n*n}\n{n} * {n} * {n} = {n*n*n}"))
    while len(cases) < 100:
        n = random.randint(-1000, 1000)
        cases.append((f"{n}", f"{n} * {n} = {n*n}\n{n} * {n} * {n} = {n*n*n}"))
    write_tests("h01pow23/test.txt", cases)

def gen_H02FSQRT():
    cases = []
    for x in [0.0, 1.0, 2.25]:
        cases.append((f"{x:.6f}", f"sqrt({x}) = {math.sqrt(x):.6f}"))
    while len(cases) < 100:
        x = random.uniform(0, 10000)
        cases.append((f"{x:.6f}", f"sqrt({x}) = {math.sqrt(x):.6f}"))
    write_tests("h02fsqrt/test.txt", cases)

def gen_H03LIEQ():
    cases = []
    cases.append(("0 0", "Solution is any number"))
    cases.append(("0 5", "No solutions"))
    cases.append(("0 -30", "No solutions"))
    cases.append(("5 10", f"x = {-10/5:.6f}"))
    while len(cases) < 100:
        A = random.randint(-10, 10)
        B = random.randint(-10, 10)
        if A == 0 and B == 0:
            ans = "Solution is any number"
        elif A == 0:
            ans = "No solutions"
        else:
            ans = f"x = {-B/A:.6f}"
        cases.append((f"{A} {B}", ans))
    write_tests("h03lieq/test.txt", cases)

def gen_H04SORT3():
    cases = []
    for triple in [(1, 3, 2), (5, 1, -2), (1, 30, 1)]:
        cases.append(("{} {} {}".format(*triple), "{} {} {}".format(*sorted(triple))))
    while len(cases) < 100:
        arr = [random.randint(-100, 100) for _ in range(3)]
        cases.append((f"{arr[0]} {arr[1]} {arr[2]}", "{} {} {}".format(*sorted(arr))))
    write_tests("h04sort3/test.txt", cases)

def gen_H05GERON():
    special = [
        (0, 5, 5),
        (-1, 2, 3),
        (1, 2, 3),
        (1, 3, 2),
        (3, 1, 2),
        (1, 1, 2),
        (2, 4, 2),
        (3, 4, 5),
        (5, 12, 13)
    ]
    tests = []
    for a, b, c in special:
        if a + b > c and a + c > b and b + c > a and a > 0 and b > 0 and c > 0:
            s = (a + b + c) / 2
            area = math.sqrt(s * (s - a) * (s - b) * (s - c))
            tests.append((f"{a} {b} {c}", f"s = {area:.6f}"))
        else:
            tests.append((f"{a} {b} {c}", "Not triangle"))
    while len(tests) < 100:
        a = round(random.uniform(0.1, 100.0), 2)
        b = round(random.uniform(0.1, 100.0), 2)
        c = round(random.uniform(0.1, 100.0), 2)
        if a + b > c and a + c > b and b + c > a and a > 0 and b > 0 and c > 0:
            s = (a + b + c) / 2
            area = math.sqrt(s * (s - a) * (s - b) * (s - c))
            tests.append((f"{a} {b} {c}", f"s = {area:.6f}"))
        else:
            tests.append((f"{a} {b} {c}", "Not triangle"))
    write_tests("h05geron/test.txt", tests)

def gen_H06SUM():
    cases = []
    cases.append(("1 1", "1"))
    cases.append(("1 5", "15"))
    cases.append(("5 1", "0"))
    while len(cases) < 100:
        A = random.randint(-100, 100)
        B = random.randint(-100, 100)
        if A <= B:
            s = sum(range(A, B + 1))
        else:
            s = 0
        cases.append((f"{A} {B}", str(s)))
    write_tests("h06sum/test.txt", cases)

def gen_H07FTRL():
    cases = []
    cases.append(("0", "1"))
    cases.append(("1", "1"))
    cases.append(("5", "120"))
    while len(cases) < 100:
        N = random.randint(0, 20)
        fact = math.factorial(N)
        cases.append((str(N), str(fact)))
    write_tests("h07ftrl/test.txt", cases)

def gen_T03GCD():
    cases = []
    special = [
        (0, 0),
        (0, 5),
        (5, 0),
        (1, 7),
        (7, 1),
        (5, 5),
        (-5, 5),
        (5, -5),
        (-5, -5),
        (17, 13),
        (12, 18),
        (100000000, 50000000)
    ]
    for a, b in special:
        g = math.gcd(a, b)
        if a == 0 or b == 0:
            l = 0
        else:
            l = abs(a // g * b)
        cases.append((f"{a} {b}", f"gcd = {g}\nlcm = {l}"))
    while len(cases) < 100:
        a = random.randint(-1000, 1000)
        b = random.randint(-1000, 1000)
        g = math.gcd(a, b)
        l = 0 if a == 0 or b == 0 else abs(a // g * b)
        cases.append((f"{a} {b}", f"gcd = {g}\nlcm = {l}"))
    write_tests("t03gcd/test.txt", cases)

if __name__ == '__main__':
    gen_H01POW23()
    gen_H02FSQRT()
    gen_H03LIEQ()
    gen_H04SORT3()
    gen_H05GERON()
    gen_H06SUM()
    gen_H07FTRL()
    gen_T03GCD()


