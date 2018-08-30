import random
import time

import gym
from gym import spaces, error
from gym.utils import seeding
from numpy import array

from .hearts_core import *
from .bot import RandomBot, SequentialBot
from .action_space import ActionSpace

from .rule_bot import GameInfo, ChunTingBot
from .card import INT_TO_RANK, RANK_TO_INT

INT_TO_SUIT = ['S', 'H', 'D', 'C']
def convert_array_to_card(array_card):
    if not array_card:
        return None
    if array_card == (-1, -1):
        return None
    r, s = array_card[0], array_card[1]
    rank = INT_TO_RANK[r+2]
    suit = INT_TO_SUIT[s]
    return rank+suit

class SingleEnv(gym.Env):
    PLAYER = 3

    def __init__(self):
        self.n_seed = None
        self.observation_space = spaces.Tuple([
            # player states
            spaces.Tuple([
                spaces.Tuple([ # p0, p1, p2
                    spaces.Discrete(200), # score
                    spaces.Tuple([ # income
                        spaces.MultiDiscrete([13, 4])
                    ] * 52),
                ] * 3),
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

        self.bots = [ChunTingBot() for _ in range(3)]

    def seed(self, seed=None):
        _, seed = seeding.np_random(seed)
        self.n_seed = seed
        random.seed(seed)
        return [seed]

    def render(self, mode='human', close=False):
        self._table.render()

    def _pack_obs_to_info(self):
        info = GameInfo()

        action_sapce = ActionSpace(self._table, self._table.cur_pos)
        cards = action_sapce.get_all_valid_actions()
        for card in cards:
            if card != (-1, -1):
                info.candidate.append(convert_array_to_card(card))
        #logger.debug('pos %r candidate %r' % (self._table.cur_pos, info.candidate))

        info.table.heart_exposed = self._table.heart_exposed
        info.table.exchanged = self._table.exchanged
        info.table.n_round = self._table.n_round + 1
        info.table.n_game = self._table.n_games
        info.table.first_draw = convert_array_to_card(self._table.first_draw) if self._table.first_draw else None
        info.table.finish_expose = self._table.finish_expose
        info.me = self._table.cur_pos

        for idx, card in enumerate(self._table.board):
            info.table.board[idx] = convert_array_to_card(card)

        for idx, player in enumerate(self._table.players):
            if idx == info.me:
                for card in player.hand:
                    info.players[idx].hand.add_card(convert_array_to_card(card))
                #logger.debug('pos %r hand %r' % (self._table.cur_pos, info.players[idx].hand.df))
            for card in player.income:
                info.players[idx].income.add_card(convert_array_to_card(card))
                info.table.opening_card.add_card(convert_array_to_card(card))

        if info.table.first_draw:
            for idx, card in enumerate(info.table.board):
                if card and card[1] != info.table.first_draw[1]:
                    info.players[idx].no_suit.add(info.table.first_draw[1])

        return info

    def _push_turn(self):
        while self._table.cur_pos != self.PLAYER:
            cur_pos = self._table.cur_pos
            player = self._table.players[cur_pos]

            info = self._pack_obs_to_info()
            draws = self.bots[cur_pos].declare_action(info)
            logger.debug('[push turn] cur_pos %r', cur_pos)
            try:
                if type(draws) is str:
                    draws = [draws]
                draws = [(RANK_TO_INT[c[0]]-2, INT_TO_SUIT.index(c[1])) for c in draws]
                done = self._table.step((cur_pos, draws))
            except Exception:
                action_space = ActionSpace(self._table, cur_pos)
                draws = [(c[0], c[1]) for c in action_space.sample()]
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

        score_before = 0 if self._table.n_round == 0 else score_before
        rewards = score_after - score_before
        
        # TODO Maybe can return some debug info
        return self._get_current_state(), rewards, done, {}

    def _pad(self, l, n, v):
        if (not l) or (l is None):
            l = []
        return l + [v] * (n - len(l))


    def _get_current_state(self):
        opponent_features = []
        for i in range(self.PLAYER):
            opponent_income = []
            for card in self._table.players[i].income:
                opponent_income.append(array(card))
            opponent_income = self._pad(opponent_income, 52, array((-1, -1)))

            opponent_features += [
                int(self._table.players[i].score),
                tuple(opponent_income),
            ]

        player_states = [tuple(opponent_features)]

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
        self.last_first_draw = None
        self._table.game_start()
        self._push_turn()
        return self._get_current_state()


