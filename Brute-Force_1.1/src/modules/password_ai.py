# src/core/password_ai.py

import collections

def rank_passwords(password_list):
    length_sorted = sorted(password_list, key=len)
    counter = collections.Counter(length_sorted)
    ranked = [item for item, _ in counter.most_common()]
    return ranked

def simple_markov(password_list):
    transitions = collections.defaultdict(lambda: collections.defaultdict(int))
    for pw in password_list:
        for a, b in zip(pw, pw[1:]):
            transitions[a][b] += 1
    def score(pw):
        return sum(transitions[a][b] for a, b in zip(pw, pw[1:]))
    return sorted(password_list, key=score, reverse=True)

