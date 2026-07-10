import random

def get_shuffled_seeds():
    seeds = [f"{chr(65 + i)}{j}" for i in range(8) for j in (1, 2)]  
    random.shuffle(seeds)
    return seeds

print(get_shuffled_seeds())