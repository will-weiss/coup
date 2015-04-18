import random
import collections

class PublicPlayer:
    def __init__(self, player):
        self.name = player.name
        self.coins = player.coins
        self.get_role = player.get_role
        self.lose_role = player.lose_role
        self.cycle_role = player.cycle_role
        self.assign_roles = player.assign_roles
        self.lives_left = player.lives_left
        self.choose_action_and_target = player.choose_action_and_target
        self.choose_reaction = player.choose_reaction
        self.exchange = player.exchange
        self.choose_reveal = player.choose_reveal
        self.choose_response = player.choose_response
        self.lose_influence = player.lose_influence

class Player:
    def __init__(self, name, game):
        self.name = name
        self.game = game
        self.coins = 2
        self.assign_roles(2)
        self.public = PublicPlayer(self)

    def get_role(self, role = None):
        if role is None:
            role = self.game.deck.deal()
        self.roles[role] += 1
        return role

    def lose_role(self, role):
        self.roles[role] -= 1
        if not self.roles[role]:
            self.roles.pop(role)
        return role

    def cycle_role(self, role):
        self.lose_role(role)
        self.get_role(self.game.deck.cycle(role))

    def assign_roles(self, num):
        self.roles = collections.defaultdict(int)
        for i in range(num):
            self.get_role()

    @property
    def lives_left(self):
        return sum(self.roles.values())

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
                if set(self.roles.keys()).intersection(action.counter_roles):
                    return 'counter'
                else:
                    return 'counter' if r < .01 else None
        return 'challenge' if r < .05 else 'counter' if r < .07 else None

    def exchange(self):
        role = random.choice(self.roles.keys())
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
        lost_role = random.choice(self.roles.keys())
        return self.lose_role(lost_role)

