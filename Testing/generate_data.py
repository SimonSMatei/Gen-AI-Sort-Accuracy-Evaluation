from random import randint as r
import os

script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
os.makedirs(script_dir, exist_ok=True)

TRIAL_NUM = 50

with open(os.path.join(script_dir, "lists_small.txt"), "w") as file:
    for i in range(0, TRIAL_NUM):
        file.write(f"{[r(1, 10000) for i in range(0, 10)]}\n")

with open(os.path.join(script_dir, "lists_medium.txt"), "w") as file:
    for i in range(0, TRIAL_NUM):
        file.write(f"{[r(1, 10000) for i in range(0, 100)]}\n")

with open(os.path.join(script_dir, "lists_large.txt"), "w") as file:
    for i in range(0, TRIAL_NUM):
        file.write(f"{[r(1, 10000) for i in range(0, 500)]}\n")

with open(os.path.join(script_dir, "lists_duplicates.txt"), "w") as file:
    for i in range(0, TRIAL_NUM):
        file.write(f"{[r(1, 10) for i in range(0, 100)]}\n")
