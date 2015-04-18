import random
import collections


class Player:

    def __init__(self, name, game):
        self.name = name
        self.game = game
        self.coins = 2
        self.assign_roles(2)

    def get_role(self, role = None):
        if role is None:
            role = self.game.deck.deal()
        self.__roles[role] += 1
        return role

    def lose_role(self, role):
        self.__roles[role] -= 1
        if not self.__roles[role]:
            self.__roles.pop(role)
        return role

    def cycle_role(self, role):
        self.lose_role(role)
        self.get_role(self.game.deck.cycle(role))

    def assign_roles(self, num):
        self.__roles = collections.defaultdict(int)
        for i in range(num):
            self.get_role()

    def match_roles(self, roles):
        return roles.intersection(self.__roles)

    @property
    def lives_left(self):
        return sum(self.__roles.values()) or 0

    def choose_action_and_target(self):
        actions_available = [a for a in self.game.actions.values() if (a.net_coins + self.coins >= 0)]
        action = random.choice(actions_available)
        target = random.choice(self.game.other_players) if action.targetable else None
        return (action, target)

    def choose_reaction(self, player, action, target):
        r = random.random()
        if action.specific_role is None:
            if action.counter_roles is None:
                return None
            else:
                if set(self.__roles.keys()).intersection(action.counter_roles):
                    return 'counter'
                else:
                    return 'counter' if r < .01 else None
        return 'challenge' if r < .05 else 'counter' if r < .07 else None

    def exchange(self):
        role = random.choice(self.__roles.keys())
        self.cycle_role(role)

    def choose_reveal(self, matching_roles):
        role = random.choice(list(matching_roles))
        self.cycle_role(role)

    def choose_response(self, action, player, target):
        r = random.random()
        if r < .05:
            return 'challenge'
        else:
            return None

    def lose_influence(self):
        if self.lives_left:
            lost_role = random.choice(self.__roles.keys())
            return self.lose_role(lost_role)
