import random

def generate_test_case(a, b):
    return f"""####### TEST CASE #######
{a}
{b}
---
{a} + {b} = {a + b}
"""

def generate_tests(filename, count=1000):
    with open(filename, 'w', encoding='utf-8') as f:
        # Special cases
        special_cases = [
            (0, 0),
            (1, 1),
            (-1, -1),
            (999999, 1),
            (-999999, 1),
        ]
        
        for a, b in special_cases:
            f.write(generate_test_case(a, b))
        
        # Random tests
        for _ in range(count - len(special_cases)):
            a = random.randint(-1000000, 1000000)
            b = random.randint(-1000000, 1000000)
            
            # 10% of tests on big numbers
            if random.random() < 0.1:
                a *= 1000
                b *= 1000
            
            f.write(generate_test_case(a, b))

if __name__ == "__main__":
    generate_tests("test.txt")
    print("Generation completed. Tests saved in 'test.txt'")
