import random
import time

import gym
from gym import spaces, error
from gym.utils import seeding
from numpy import array

from .hearts_core import *
from .bot import RandomBot

class SingleEnv(gym.Env):
    PLAYER = 3

    def __init__(self):
        self.n_seed = None
        self.observation_space = spaces.Tuple([
            # player states
            spaces.Tuple([
                spaces.Discrete(200), # score
                spaces.Tuple([ # hand
                    spaces.MultiDiscrete([13, 4])
                ] * 13),
                spaces.Tuple([ # income
                    spaces.MultiDiscrete([13, 4])
                ] * 52),
            ] * 4),
            # table states
            spaces.Tuple([
                spaces.Discrete(13), # n_round
                spaces.Discrete(4), # start_pos
                spaces.Discrete(4), # cur_pos
                spaces.Discrete(1), # exchanged
                spaces.Discrete(1), # heart_occured
                spaces.Discrete(100), # n_games
                spaces.Tuple([ # board
                    spaces.MultiDiscrete([13, 4])
                ] * 4),
                spaces.Tuple([ # first_draw
                    spaces.MultiDiscrete([13, 4])
                ]),
                spaces.Tuple([ # bank
                    spaces.Tuple([
                        spaces.MultiDiscrete([13, 4])
                    ] * 3),
                ] * 4)
            ]),
        ])

        self.action_space = spaces.Tuple([
            spaces.Discrete(4), # cur_pos
            spaces.Tuple([ # bank(3) draw(1)
                spaces.MultiDiscrete([13, 4])
            ] * 3),
        ])

        self.bots = [RandomBot(i) for i in range(3)]

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
            obs = self._get_current_state()
            player_obs = tuple([obs[0][i]] for i in range(cur_pos*3, cur_pos*3+3))
            action = self.bots[cur_pos].declare_action(player_obs, obs[1])
            self._table.step(self._convert_actspace_act(action))

    def _convert_actspace_act(self, action):
        draws = []
        cur_pos, card_array = action
        for card in card_array:
            rank = card[0]
            suit = card[1]
            if rank >= 0 and suit >= 0:
                draws.append((rank, suit))
        return (cur_pos, draws)

    def _convert_act_actspace(self, action):
        cur_pos, draws = action
        action_s = [cur_pos]
        cards = []
        for draw in draws:
            cards.append(array([draw[0], draw[1]]))
        cards = self._pad(cards, 3, array([-1, -1]))
        action_s.append(tuple(cards))
        return tuple(action_s)


    def step(self, action):
        if not self.action_space.contains(action):
            raise error.Error('Invalid action')
        
        cur_pos, card_array = action
        score_before = self._table.players[cur_pos].get_rewards()
        
        done = self._table.step(self._convert_actspace_act(action))
        self._push_turn()

        score_after = self._table.players[cur_pos].get_rewards()
        # XXX I think this is too simple
        rewards = score_after - score_before
        
        # TODO Maybe can return some debug info
        return self._get_current_state(), rewards, done, {}

    def _pad(self, l, n, v):
        if (not l) or (l is None):
            l = []
        return l + [v] * (n - len(l))


    def _get_current_state(self):
        player_states = []
        for idx, player in enumerate(self._table.players):
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

            # Tuple: [int], ([r, s], [r, s], ...), ([r, s], [r, s], ...)
            player_features += [tuple(player_hand), tuple(player_income)]
            player_states += player_features

        table_states = [
            int(self._table.n_round),
            int(self._table.start_pos),
            int(self._table.cur_pos),
            int(self._table.exchanged),
            int(self._table.heart_occur),
            int(self._table.n_games),
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
        for cards in self._table.bank:
            bank = []
            if cards:
                for card in cards:
                    bank.append(array(card))
            bank = self._pad(bank, 3, array((-1, -1)))
            banks.append(tuple(bank))

        table_states += [tuple(boards), tuple(first_draw), tuple(banks)]

        return (tuple(player_states), tuple(table_states))

    def reset(self):
        self._table = Table(self.n_seed)
        self._table.game_start()
        self._push_turn()
        return self._get_current_state()


