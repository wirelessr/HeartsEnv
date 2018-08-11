import random

import gym
from gym import spaces

from hearts_core import *

class HeartsEnv(gym.Env):
    def __init__(self):
        # TODO
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
        self.action_space = spaces.Tuple([
            spaces.Discrete(4),
            spaces.Tuple([
                spaces.Discrete(13),
                spaces.Discrete(4),
            ]),
        ])


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


