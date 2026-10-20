"""Random test generator for stress.py.

stress.py runs this as:  python3 gen.py <seed>
Print ONE test case to stdout. Keep cases small: the brute force has to finish
on them, and most bugs show up on small inputs anyway.
"""
import random
import sys

random.seed(int(sys.argv[1]))

n = random.randint(1, 8)
print(n)
print(*(random.randint(1, 10) for _ in range(n)))
