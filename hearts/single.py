import random
import time

import gym
from gym import spaces, error
from gym.utils import seeding
from numpy import array

from .hearts_core import *
from .bot import RandomBot, SequentialBot
from .action_space import ActionSpace

class SingleEnv(gym.Env):
    PLAYER = 3

    def __init__(self):
        self.n_seed = None
        self.observation_space = spaces.Tuple([
            # player states
            spaces.Tuple([
                spaces.Discrete(200), # p0 score
                spaces.Discrete(200), # p1 score
                spaces.Discrete(200), # p2 score
                spaces.Discrete(200), # p3 score
                spaces.Tuple([ # hand
                    spaces.MultiDiscrete([13, 4])
                ] * 13),
                spaces.Tuple([ # income
                    spaces.MultiDiscrete([13, 4])
                ] * 52),
            ]),
            # table states
            spaces.Tuple([
                spaces.Discrete(13), # n_round
                spaces.Discrete(4), # start_pos
                spaces.Discrete(4), # cur_pos
                spaces.Discrete(1), # exchanged
                spaces.Discrete(1), # heart_occured
                spaces.Discrete(100), # n_games
                spaces.Discrete(1), # finish_expose
                spaces.Discrete(1), # heart_exposed
                spaces.Tuple([ # board
                    spaces.MultiDiscrete([13, 4])
                ] * 4),
                spaces.Tuple([ # first_draw
                    spaces.MultiDiscrete([13, 4])
                ]),
                spaces.Tuple([ # backup
                    spaces.MultiDiscrete([13, 4])
                ] * 4)
            ]),
        ])

        self.action_space = spaces.Tuple([ # bank(3) draw(1)
            spaces.MultiDiscrete([13, 4])
        ] * 3)

        self.bots = [random.choice([SequentialBot(i), RandomBot(i)]) for i in range(3)]

    def seed(self, seed=None):
        _, seed = seeding.np_random(seed)
        self.n_seed = seed
        random.seed(seed)
        return [seed]

    def render(self, mode='human', close=False):
        self._table.render()

    def _push_turn(self):
        while self._table.cur_pos != self.PLAYER:
            cur_pos = self._table.cur_pos
            player = self._table.players[cur_pos]

            player_hand = []
            for card in player.hand:
                player_hand.append(array(card))
            player_hand = self._pad(player_hand, 13, array((-1, -1)))

            player_income = []
            for card in player.income:
                player_income.append(array(card))
            player_income = self._pad(player_income, 52, array((-1, -1)))
            
            obs = self._get_current_state()
            player_obs = tuple([player.score, tuple([player_hand,]), tuple([player_income,])])
            logger.debug('[push turn] cur_pos %r', cur_pos)
            cur_pos, draws = self.bots[cur_pos].declare_action(player_obs, obs[1])
            draws = [(c[0], c[1]) for c in draws if not all(c == (-1, -1))]
            done = self._table.step((cur_pos, draws))
            if done:
                return True
        
        return False


    def step(self, action):
        if not self.action_space.contains(action):
            raise error.Error('Invalid action')
        
        card_array = action
        score_before = self._table.players[self.PLAYER].get_rewards()
        
        draws = [(c[0], c[1]) for c in card_array if not all(c == (-1, -1))]
        done = self._table.step((self.PLAYER, draws))
        if not done:
            done = self._push_turn()

        score_after = self._table.players[self.PLAYER].get_rewards()

        rewards = score_after - score_before
        
        # TODO Maybe can return some debug info
        return self._get_current_state(), rewards, done, {}

    def _pad(self, l, n, v):
        if (not l) or (l is None):
            l = []
        return l + [v] * (n - len(l))


    def _get_current_state(self):
        player_states = [self._table.players[i].score for i in range(self.PLAYER)] 

        player = self._table.players[self.PLAYER]
        player_features = [
            int(player.score),
        ]
        
        player_hand = []
        for card in player.hand:
            player_hand.append(array(card))
        player_hand = self._pad(player_hand, 13, array((-1, -1)))

        player_income = []
        for card in player.income:
            player_income.append(array(card))
        player_income = self._pad(player_income, 52, array((-1, -1)))

        player_features += [tuple(player_hand), tuple(player_income)]
        player_states += player_features

        table_states = [
            int(self._table.n_round),
            int(self._table.start_pos),
            int(self._table.cur_pos),
            int(self._table.exchanged),
            int(self._table.heart_occur),
            int(self._table.n_games),
            int(self._table.finish_expose),
            int(self._table.heart_exposed),
        ]

        boards = []
        for card in self._table.board:
            if card:
                boards.append(array(card))
            else:
                boards.append(array((-1, -1)))

        first_draw = [array(self._table.first_draw)] if self._table.first_draw\
                else [array((-1, -1))]

        banks = []
        for card in self._table.backup:
            if card:
                banks.append(array(card))
            else:
                banks.append(array((-1, -1)))

        table_states += [tuple(boards), tuple(first_draw), tuple(banks)]

        self.action_space = ActionSpace(self._table, self.PLAYER)
        return (tuple(player_states), tuple(table_states))

    def reset(self):
        self._table = Table(self.n_seed)
        self._table.game_start()
        self._push_turn()
        return self._get_current_state()


