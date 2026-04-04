import random

def generate_words(words: list, n: int) -> list:
    chosen_words = random.choices(words, k=n)
    return " ".join(chosen_words)