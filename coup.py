import random
import collections
import itertools

def getName(obj):
    try:
        return obj.name
    except Exception:
        return None

class Deck:
    def __init__(self, roles, num):
        self.remaining = []
        for role in roles:
            for i in range(num):
                self.add(role)
        self.shuffle()

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

class Action:
    def __init__(self, net_coins, specific_role, counter_roles, role_exchange, target_coin_loss, target_influence_loss):
        self.net_coins = net_coins
        self.specific_role = specific_role
        self.counter_roles = counter_roles
        self.role_exchange = role_exchange
        self.target_coin_loss = target_coin_loss
        self.target_influence_loss = target_influence_loss

    @property
    def targetable(self):
        return (self.target_coin_loss or self.target_influence_loss)

class Role:
    def __init__(self, name):
        self.name = name
        self.actions = {}
        self.counters = {}

class Player:
    def __init__(self, name, game):
        self.name = name
        self.game = game
        self.coins = 2
        self.assign_roles(2)

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
        target = random.choice(self.game.rotation) if action.targetable else None
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

class Game:
    def __init__(self, names):
        self.info = []
        self.roles = dict((r, Role(r)) for r in ['ambassador', 'assassin', 'captain', 'contessa', 'duke'])
        self.num_cards_per_role = 3
        self.deck = Deck(self.roles, self.num_cards_per_role)
        self.turn_no = 0
        self.actions = {
            'income'      : Action(1 , None        , None                          , False, 0, False),
            'foreign_aid' : Action(2 , None        , set(['duke'])                 , False, 0, False),
            'coup'        : Action(-7, None        , None                          , False, 0, True),
            'tax'         : Action(3 , 'duke'      , None                          , False, 0, False),
            'assassinate' : Action(-3, 'assassin'  , set(['contessa'])             , False, 0, True),
            'exchange'    : Action(0 , 'ambassador', None                          , True , 0, False),
            'steal'       : Action(2 , 'captain'   , set(['captain', 'ambassador']), False, 2, False)
        }
        for action_name, action in self.actions.iteritems():
            action.name = action_name
            if action.specific_role:
                self.roles[action.specific_role].actions[action_name] = action
            for role in (action.counter_roles or []):
                self.roles[role].counters[action_name] = action
        self.players = dict((name, Player(name, self)) for name in names)
        self.setup_rotation(names)

    def setup_rotation(self, names):
        self.rotation = collections.deque([self.players[name] for name in names], len(names))

    def log(self, msg):
        self.info.append(msg)

    @property
    def current_player(self):
        return self.rotation[0]

    @property
    def other_players(self):
        return list(itertools.islice(self.rotation, 1, len(self.rotation)))

    # True if the challengee has a required role
    def determine_challenge_result(self, roles, challengee, challenger):
        matching_roles = set(roles).intersection(challengee.roles)
        if len(matching_roles):
            challengee.choose_reveal(matching_roles)
            challenger.lose_influence()
            return True
        else:
            challengee.lose_influence()
            return False

    def potentially_remove_player(self, player):
        if not player.lives_left:
            self.setup_rotation([p.name for p in self.rotation if not p is player])
            return True
        return False

    def resolve_action(self, action, player, target):
        player.coins += action.net_coins
        if target:
            target.coins -= action.target_coin_loss
            if action.target_influence_loss:
                target.lose_influence()
                self.potentially_remove_player(target)
        if action.role_exchange:
            player.exchange()

    def turn(self):
        (action, target) = self.current_player.choose_action_and_target()
        self._action = action
        resolve = True
        reaction = None
        response = None
        for other_player in self.other_players:
            reaction = other_player.choose_reaction(self.current_player, action, target)
            if reaction is None:
                continue
            elif reaction is 'challenge':
                resolve = self.determine_challenge_result(set([action.specific_role]), self.current_player, other_player)
            elif reaction is 'counter':
                response = self.current_player.choose_response(action, other_player, target)
                if response is 'challenge':
                    resolve = not self.determine_challenge_result(action.counter_roles, other_player, self.current_player)
                else:
                    resolve = False
            if resolve:
                self.potentially_remove_player(other_player)
            break

        if resolve:
            self.resolve_action(action, self.current_player, target)

        if not self.potentially_remove_player(self.current_player):
            self.rotation.rotate(-1)

        self.log({
            'turn_no'        : self.turn_no,
            'current_player' : getName(self.current_player),
            'action'         : getName(action),
            'target'         : getName(target),
            'reaction'       : reaction,
            'response'       : response
        })
        self.turn_no += 1

    def play(self):
        while len(self.rotation) > 1:
            self.turn()
        self.log("WINNER: {0}".format(self.rotation[0].name))

game = Game(['will', 'pat', 'frank'])

game.play()



