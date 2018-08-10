import random

import gym
from gym import spaces

# 0:s, 1:h, 2:d, 3:c (-1: None)
# 0:2, 1:3, ..., 8:T, 9:J, 10:Q, 11:K, 12:A (-1: None)
deck = [(rank, suit) for rank in range(13) for suit in range(4)]
n_seats = 4
n_pocket_cards = 13

def _pad(self, l, n, v):
    if (not l) or (l is None):
        l = []
    return l + [v] * (n - len(l))

class Player(object):
    def __init__(self, idx, cards):
        self._idx = idx
        self.hand = cards
        self.income = []

class Table(object):
    def __init__(self, players):
        self._player = players
        self.n_round = 0
        self.board = [(-1, -1)] * n_seats
        for idx, player in enumerate(self._player):
            if (0, 3) in player.hand:
                self.start_pos = idx
                break


class HeartsEnv(gym.Env):
    def __init__(self):
        self._deck = []
        self._player = []
        self._round = 0
        self._table = None

        self.observation_space = spaces.Tuple([
            # player states
            spaces.Tuple([
                spaces.MultiDiscrete([
                    200, # score
                    1, # your turn
                    4, # pos
                ]),
                spaces.Tuple([ # hand
                    spaces.MultiDiscrete([13, 4])
                ] * 13),
                spaces.Tuple([ # income
                    spaces.MultiDiscrete([13, 4])
                ] * 52),
            ] * n_seats),
            # table states
            spaces.Tuple([
                spaces.Discrete(n_pocket_cards), # rounds
                spaces.Discrete(n_seats), # start pos
                spaces.Tuple([ # draws
                    spaces.MultiDiscrete([13, 4]),
                ] * n_seats)
            ]),
        ])
        # TODO
        self.action_space = spaces.Discrete(2)


    # TODO
    def step(obs):
        return cur_obs, reward, isfinish, info

    def _get_current_state(self):
        player_states = []
        for idx, player in enumerate(self._player):
            player_features = [
                int(player.score),
                int(player.isYourTurn),
                int(idx),
            ]
            player_states.append((player_features, player.get_hand(), player.get_income())) # Tuple: [int, int], ([r, s], [r, s], ...), ([r, s], [r, s], ...)
        table_states = ([
            int(self._table.n_round),
            int(self._table.start_pos)
        ], self._table.board)
        # XXX
        return (tuple(player_states), table_states)

    def reset(self):
        self._deck = deck
        random.shuffle(self._deck)
        self._player = [Player(i, self._deck[i*n_pocket_cards : (i+1)*n_pocket_cards]) for i in range(4)]
        self._table = Table(self._player)
        return self._get_current_state()


