# encoding: utf-8
import random
import pandas as pd
import numpy as np

from .system_log import system_log
from .card import Cards, INT_TO_RANK, RANK_TO_INT

class PlayerInfo:

    def __init__(self):
        self.no_suit = set()
        self.income = Cards()
        self.draw = Cards()
        self.hand = Cards()
        self.name = ''
        self.round_score = 0
        self.valid_action = Cards()

    def to_array(self):
        # S, H, D, C
        suit = [-1, -1, -1, -1]
        if 'S' in self.no_suit:
            suit[0] = 1
        elif 'H' in self.no_suit:
            suit[1] = 1
        elif 'D' in self.no_suit:
            suit[2] = 1
        elif 'C' in self.no_suit:
            suit[3] = 1
        t = [self.round_score] + suit
        return np.array(t + self.income.df.values.reshape(1, 52)[0].tolist() + self.draw.df.values.reshape(1, 52)[0].tolist())


class TableInfo:

    def __init__(self):
        self.heart_exposed = False
        self.exchanged = False
        self.n_round = 0
        self.n_game = 0
        self.board = [None, None, None, None]
        self.first_draw = None
        self.opening_card = Cards()
        self.finish_expose = False

    def to_array(self):
        return np.array([self.n_game, self.n_round])


class GameInfo:

    def __init__(self):
        # Major
        self.players = [PlayerInfo() for _ in range(4)]
        self.table = TableInfo()
        self.me = -1
        # Minor
        self.pass_to = ''
        self.receive_from = ''
        self.picked = []
        self.received = []
        self.who_exposed = -1
        self.candidate = []

    def get_pos(self):
        # (0, 1, 2, 3)
        return 4 - self.table.board.count(None)

    def get_board_score(self):
        score = 0
        for card in self.table.board:
            if card == 'QS':
                score += 13
            elif card and card[1] == 'H':
                score += 1
        return score

    def get_board_max(self):
        max_rank = RANK_TO_INT[self.table.first_draw[0]]
        for card in self.table.board:
            if card:
                r, s = card
                r = RANK_TO_INT[r]
                if s == self.table.first_draw[1]:
                    if r > max_rank:
                        max_rank = r
        return max_rank

    def get_possiable_min(self, n):
        card = None

        if self.table.first_draw:
            max_rank = RANK_TO_INT[self.candidate[0][0]]
            suit = self.candidate[0][1]
            max_board = self.get_board_max()
            for r, s in self.candidate:
                r = RANK_TO_INT[r]
                if s == self.table.first_draw[1] and r <= max_board and r >= max_rank:
                    max_rank = r
                    suit = s
            system_log.show_message(u'後手：挑最大的安全牌出')
            return '%s%s' % (INT_TO_RANK[max_rank], suit)
        else:
            world_cards = self.players[self.me].hand.df + self.table.opening_card.df
            max_less = 0
            max_target = None
            for r, s in self.candidate:
                r = RANK_TO_INT[r]
                wc = list(world_cards.loc[world_cards[s] == 0].index)
                lc = filter(lambda x: x < r, wc)

                less_count = len(list(lc))
                if less_count <= n and less_count >= max_less:
                    max_less = less_count
                    max_target = '%s%s' % (INT_TO_RANK[r], s)

            system_log.show_message(u'先手：挑小的出')
            return max_target

        return card

    def to_array(self):
        t = np.array([])
        for p in self.players:
            t = np.append(t, p.to_array())
        return np.append(t, self.table.to_array())


class ChunTingBot():
    def declare_action(self, info):
        my_hand = info.players[info.me].hand.df
        columns = info.players[info.me].hand.columns

        if not info.table.exchanged and info.table.n_game % 4 != 0:
            pass_card = set()

            topS = filter(lambda x: x >= 12, list(my_hand[my_hand['S'] > 0].index))
            for s in topS:
                pass_card.add('%sS' % INT_TO_RANK[s])
                system_log.show_message(u'換掉黑桃大牌 %r' % pass_card)

            if len(pass_card) != 3:
                totals = list(my_hand.sum())
                for i, count in enumerate(totals):
                    if i == columns.index('S'):
                        continue
                    if count <= 3 - len(pass_card):
                        for rank in list(my_hand[my_hand[columns[i]] > 0].index):
                            pass_card.add('%s%s' % (INT_TO_RANK[rank], columns[i]))
                            system_log.show_message(u'除了黑桃，如果剛好可以缺門就拼缺門 %r' % pass_card)

            if len(pass_card) != 3:
                for suit in ['C', 'H', 'D']:
                    tops = filter(lambda x: x >= 12, sorted(list(my_hand[my_hand[suit] > 0].index), reverse=True))
                    for s in tops:
                        if len(pass_card) < 3:
                            pass_card.add('%s%s' % (INT_TO_RANK[s], suit))
                            system_log.show_message(u'如果還沒滿，換掉Ｑ以上的大牌 %r' % pass_card)

            if len(pass_card) != 3:
                system_log.show_message(u'隨便啦')
                while len(pass_card) != 3:
                    pass_card.add(random.choice(info.candidate))

            system_log.show_message('pass_card %r' % pass_card)
            return list(pass_card)

        elif not info.table.finish_expose:
            expose_card = ['AH']
            totals = list(my_hand.sum())
            for i, count in enumerate(totals):
                if count > 6:
                    ranks = list(my_hand[columns[i]].index)
                    tops = list(filter(lambda x: x >= 12, ranks))
                    if len(tops) > 1:
                        expose_card = []
            return expose_card
        else:
            FIRST = 0
            LAST = 3

            pos = info.get_pos()

            pick_card = None

            # 能安全丟黑桃Ｑ就丟
            if 'QS' in info.candidate:
                if info.table.first_draw and info.table.first_draw[1] != 'S':
                    return 'QS'
                if 'KS' in info.table.board or 'AS' in info.table.board:
                    return 'QS'

            if info.table.first_draw:
                if info.candidate[0][1] != info.table.first_draw[1]:
                    tops = ['AS', 'KS']

                    for card in tops:
                        if card in info.candidate:
                            system_log.show_message(u'缺門：先丟黑桃ＡＫ')
                            return card

                    totals = list(my_hand.sum())
                    try:
                        idx = totals.index(1)
                        suit = columns[idx]
                        rank = list(my_hand.loc[my_hand[suit] == 1].index)[0]
                        system_log.show_message(u'缺門：丟差一張缺門的')
                        return '%s%s' % (INT_TO_RANK[rank], suit)
                    except ValueError:
                        pass

                    if info.table.n_round != 1:
                        hearts = sorted(list(my_hand.loc[my_hand['H'] == 1].index), reverse=True)
                        if hearts:
                            system_log.show_message(u'缺門：紅心從大開始丟')
                            return '%sH' % INT_TO_RANK[hearts[0]]
                    else:
                        max_rank = 0
                        target = None
                        for cand in info.candidate:
                            if card[1] != 'H' and card != 'QS' and RANK_TO_INT[card[0]] > max_rank:
                                max_rank = RANK_TO_INT[card[0]]
                                target = card
                        system_log.show_message(u'缺門：第一回合只能丟大牌')
                        return target

                    max_rank = 0
                    target = None
                    for r,s in info.candidate:
                        r = RANK_TO_INT[r]
                        if r > max_rank:
                            max_safe = r
                            target = '%s%s' % (INT_TO_RANK[r], s)
                    system_log.show_message(u'缺門：從最大開始丟')
                    return target


            if pos == LAST:
                max_rank = info.get_board_max()
                max_safe = 0
                target = None
                for r,s in info.candidate:
                    r = RANK_TO_INT[r]
                    if s == info.table.first_draw[1] and r < max_rank and r >= max_safe:
                        max_safe = r
                        target = '%s%s' % (INT_TO_RANK[r], s)
                if target:
                    system_log.show_message(u'最後手：挑安全牌中最大的出')
                else:
                    max_rank = 0
                    for r,s in info.candidate:
                        r = RANK_TO_INT[r]
                        if s == info.table.first_draw[1] and r > max_rank:
                            max_safe = r
                            target = '%s%s' % (INT_TO_RANK[r], s)
                    system_log.show_message(u'最後手：沒安全牌，挑最大的出')

                return target

            pick_card = info.get_possiable_min(3 - pos)

            return pick_card

