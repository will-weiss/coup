import random

class Deck:
    def __init__(self, roles, num):
        self.__remaining = []
        for role in roles:
            for i in range(num):
                self.add(role)
        self.shuffle()

    @property
    def size(self):
        return len(self.__remaining)

    def shuffle(self):
        random.shuffle(self.__remaining)

    def deal(self):
        return self.__remaining.pop()

    def add(self, role):
        self.__remaining.append(role)

    def cycle(self, role):
        self.add(role)
        self.shuffle()
        return self.deal()
