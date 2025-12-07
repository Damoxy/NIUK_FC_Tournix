import random

def get_shuffled_seeds():
    seeds = [f"{chr(i)}2" for i in range(ord('A'), ord('P') + 1)]
    random.shuffle(seeds)
    return seeds
