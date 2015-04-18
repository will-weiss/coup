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
