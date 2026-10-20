"""Random input for stress.py: two small integers, one per run."""
import random
import sys

random.seed(int(sys.argv[1]))
print(random.randint(-20, 20), random.randint(-20, 20))
