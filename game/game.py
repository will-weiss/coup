import collections
import itertools
from components.action import Action
from components.deck import Deck
from components.player import Player
from components.role import Role

def getName(obj):
    try:
        return obj.name
    except Exception:
        return None

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
        self.setup_rotation(names)
        self.players = dict((name, Player(name, self)) for name in names)

    def setup_rotation(self, names):
        self.rotation = collections.deque(names, len(names))

    def log(self, msg):
        self.info.append(msg)

    @property
    def current_player(self):
        return self.players[self.rotation[0]]

    @property
    def other_players(self):
        return [self.players[name] for name in itertools.islice(self.rotation, 1, len(self.rotation))]

    # True if the challengee has a required role
    def determine_challenge_result(self, roles, challengee, challenger):
        matching_roles = challengee.match_roles(set(roles))
        if len(matching_roles):
            challengee.choose_reveal(matching_roles)
            challenger.lose_influence()
            return True
        else:
            challengee.lose_influence()
            return False

    def trim_players(self):
        names = { 'alive': [], 'dead': [] }
        for name in self.rotation:
            t = 'alive' if self.players[name].lives_left else 'dead'
            names[t].append(name)
        self.setup_rotation(names['alive'])
        return names['dead']

    def resolve_action(self, action, player, target):
        player.coins += action.net_coins
        if target:
            target.coins -= action.target_coin_loss
            if action.target_influence_loss:
                target.lose_influence()
                self.trim_players()
        if action.role_exchange:
            player.exchange()

    def turn(self):
        cp = self.current_player
        (action, target) = cp.choose_action_and_target()
        resolve = True
        reaction = None
        response = None
        for other_player in self.other_players:
            reaction = other_player.choose_reaction(cp, action, target)
            if reaction is None:
                continue
            elif reaction is 'challenge':
                resolve = self.determine_challenge_result(set([action.specific_role]), cp, other_player)
            elif reaction is 'counter':
                response = cp.choose_response(action, other_player, target)
                if response is 'challenge':
                    resolve = not self.determine_challenge_result(action.counter_roles, other_player, cp)
                else:
                    resolve = False
            if resolve:
                self.trim_players()
            break

        if resolve:
            self.resolve_action(action, cp, target)

        removed_players = self.trim_players()
        if not cp in removed_players:
            self.rotation.rotate(-1)

        self.log({
            'turn_no'        : self.turn_no,
            'current_player' : getName(cp),
            'action'         : getName(action),
            'target'         : getName(target),
            'reaction'       : reaction,
            'response'       : response
        })
        self.turn_no += 1

    def play(self):
        while len(self.rotation) > 1:
            self.turn()
        self.log("WINNER: {0}".format(self.current_player.name))

