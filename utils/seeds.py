import random

def get_shuffled_seeds():
    seeds = [f"{chr(i)}{j}" for i in range(ord('A'), ord('AF2') + 1) for j in (1, 2)]
    random.shuffle(seeds)
    return seeds
