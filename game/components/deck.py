import random

class PrivateDeck:
    def __init__(self, roles, num):
        self.remaining = []
        for role in roles:
            for i in range(num):
                self.add(role)
        self.shuffle()

    @property
    def size(self):
        return len(self.remaining)

    def shuffle(self):
        random.shuffle(self.remaining)

    def deal(self):
        return self.remaining.pop()

    def add(self, role):
        self.remaining.append(role)

    def cycle(self, role):
        self.add(role)
        self.shuffle()
        return self.deal()

class Deck:
    def __init__(self, *args, **kwargs):
        deck = PrivateDeck(*args, **kwargs)
        self.size = deck.size
        self.shuffle = deck.shuffle
        self.deal = deck.deal
        self.add = deck.add
        self.cycle = deck.cycle
