import random
import string

def get_shuffled_seeds():
    def excel_cols(n):
        result = []
        for i in range(n):
            s = ""
            i += 1
            while i:
                i, r = divmod(i - 1, 26)
                s = chr(65 + r) + s
            result.append(s)
        return result

    cols = excel_cols(32)  # A → AF (A=1 ... AF=32)
    seeds = [f"{col}{j}" for col in cols for j in (1, 2)]
    random.shuffle(seeds)
    return seeds