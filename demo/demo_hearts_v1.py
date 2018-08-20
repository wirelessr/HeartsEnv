import sys
sys.path.append('/hearts')

import random
from numpy import array, array_equal
from hearts.bot import BotProxy, BotBase
from hearts.hearts_core import S, H, D, C
import pprint
pp = pprint.PrettyPrinter(indent=4)

class MyBot(BotBase):
    def __init__(self, idx):
        super(MyBot, self).__init__(idx)
        self.init_info()

    def init_info(self):
        self.info = {
            "idx": self.idx,
            "ex_first_draw": None,
            "unused_cards": [
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            ],
            "opponents": [
                {"ranout": [False, False, False, False]},
                {"ranout": [False, False, False, False]},
                {"ranout": [False, False, False, False]},
                {"ranout": [False, False, False, False]},
            ]
        }

    def remove_unused_cards(self, cards):
        for s in range(4):
            for r in cards[s]:
                if r in self.info["unused_cards"][s]:
                    #print("rank: {0}, suit: {1}".format(r, s))
                    self.info["unused_cards"][s].remove(r)

    def process_hand(self):
        hand = self.info["hand"]
        hearts_occur = self.info["hearts_occur"]
        start_pos = self.info["start_pos"]
        exchanged = self.info["exchanged"]
        n_round = self.info["n_round"]
        # hand
        hand_card = [[], [], [], []]
        for c in hand:
            if not array_equal(c, array([-1, -1])):
                hand_card[c[1]].append(c[0])
        if exchanged or n_round > 0:
            if not hearts_occur and self.idx == start_pos:
                hand_card[H] = []
            if hand_card == [[], [], [], []]:
                for c in hand:
                    if not array_equal(c, array([-1, -1])):
                        hand_card[c[1]].append(c[0])
        # pp.pprint(hand_card)
        for s in range(4):
            hand_card[s] = sorted(hand_card[s])
        # pp.pprint(hand_card)

        return hand_card

    def process_board(self):
        board = self.info["board"]
        # board
        board_card = [[], [], [], []]
        for c in board:
            if not array_equal(c, array([-1, -1])):
                board_card[c[1]].append(c[0])
        # pp.pprint(board_card)
        for s in range(4):
            board_card[s] = sorted(board_card[s])
        #pp.pprint(board_card)

        return board_card

    def process_bank(self):
        bank = self.info["bank"]
        ex_first_draw = self.info["ex_first_draw"]
        # bank
        bank_card = [[], [], [], []]
        try:
            p = 0
            for (r, s, c) in bank:
                bank_card[int(s)].append(int(r))
                # pp.pprint(int(s))
                # pp.pprint(ex_first_draw[1])
                if int(s) != ex_first_draw[1]:
                    self.info["opponents"][p]["ranout"][ex_first_draw[1]] = True
                p += 1
            # pp.pprint(bank_card)
            for s in range(4):
                bank_card[s] = sorted(bank_card[s])
            #pp.pprint(bank_card)
        except:
            pass

        return bank_card

    def less_suit(self):
        hand_card = self.info["hand_card"]
        # find less suit
        less_suit = C
        for s in range(3):
            if len(hand_card[less_suit]) == 0 \
                    or (len(hand_card[less_suit]) > len(hand_card[s]) \
                        and len(hand_card[s]) > 0):
                less_suit = s
        #print("less_suit: {0}".format(less_suit))

        return less_suit

    def exchange(self):
        hand_card = self.info["hand_card"]
        less_suit = self.info["less_suit"]
        draws = []
        # exchange A - Q of S
        s = S
        for r in [12,11,10]:
            if len(draws) == 3:
                break
            if r in hand_card[s]:
                draws.append(array([r, s]))
                hand_card[s].remove(r)
        #pp.pprint(draws)

        # exchange A - Q of H
        s = H
        for r in [12,11,10]:
            if len(draws) == 3:
                break
            if r in hand_card[s]:
                draws.append(array([r, s]))
                hand_card[s].remove(r)
        #pp.pprint(draws)

        # exchange A - Q of less suit
        s = less_suit
        if len(hand_card[s]) < 3:
            for r in [12, 11, 10]:
                if len(draws) == 3:
                    break
                if r in hand_card[s]:
                    draws.append(array([r, s]))
                    hand_card[s].remove(r)
        #pp.pprint(draws)

        # exchange A - 2 of all suit
        for r in [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]:
            if len(draws) == 3:
                break
            for s in range(4):
                if len(draws) == 3:
                    break
                if r in hand_card[s]:
                    #pp.pprint(r)
                    #pp.pprint(s)
                    draws.append(array([r, s]))
                    hand_card[s].remove(r)
        #pp.pprint(draws)

        return draws

    def follow(self, s):
        hand_card = self.info["hand_card"]
        board_card = self.info["board_card"]
        # follow
        l = len(hand_card[s])
        draws = []
        for i in range(l-1,-1,-1):
            if hand_card[s][i] < board_card[s][-1]:
                draws = [array([hand_card[s][i], s])]
                break

        if len(draws) == 0:
            draws = [array([hand_card[s][-1], s])]

        return draws

    def drop(self):
        hand_card = self.info["hand_card"]
        # drop
        draws = []
        if 10 in hand_card[S]:
            draws = [array([10, S])]
        elif len(hand_card[H]) > 0:
            draws = [array([hand_card[H][-1], H])]
        else:
            for r in [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]:
                if len(draws) == 1:
                    break
                for s in range(4):
                    if len(draws) == 1:
                        break
                    if r in hand_card[s]:
                        draws = [array([r, s])]

        return draws

    def first(self):
        hand_card = self.info["hand_card"]
        # first
        draws = []
        for r in range(13):
            if len(draws) == 1:
                break
            for s in range(4):
                if len(draws) == 1:
                    break
                if r in hand_card[s]:
                    draws = [array([r, s])]

        return draws

    def declare_action(self, player_obs, table_obs):
        action = [self.idx]

        score, (hand,), (income,) = player_obs
        n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game, \
        board, (first_draw,), bank = table_obs
        self.info["hand"] = hand
        self.info["board"] = board
        self.info["bank"] = bank
        self.info["hearts_occur"] = hearts_occur
        self.info["first_draw"] = first_draw
        self.info["start_pos"] = start_pos
        self.info["exchanged"] = exchanged
        self.info["n_round"] = n_round

        #pp.pprint(hand)
        #pp.pprint(board)
        #pp.pprint(bank)

        hand_card = self.process_hand()
        self.info["hand_card"] = hand_card
        less_suit = self.less_suit()
        self.info["less_suit"] = less_suit

        if not exchanged and n_game % 4 != 0:
            # 3 cards
            draws = self.exchange()
            self.init_info()
        else:
            board_card = self.process_board()
            self.info["board_card"] = board_card
            bank_card = self.process_bank()
            self.info["bank_card"] = bank_card
            self.remove_unused_cards(hand_card)
            self.remove_unused_cards(board_card)
            self.remove_unused_cards(bank_card)
            #pp.pprint(self.info)

            # 1 card
            if self.idx == start_pos and n_round == 0:
                draws = [array([0, 3])]
            elif self.idx == start_pos:
                draws = self.first()
            else:
                s = first_draw[1]
                if len(hand_card[s]) > 0:
                    draws = self.follow(s)
                else:
                    draws = self.drop()

            draws += [array([-1, -1]), array([-1, -1])]

            if array_equal(first_draw, array([-1, -1])):
                self.info["ex_first_draw"] = draws[0]
            else:
                self.info["ex_first_draw"] = first_draw
        #pp.pprint(draws)
        action.append(tuple(draws))
        return tuple(action)

if __name__ == '__main__':
    proxy = BotProxy(0)
    proxy.add_bot(3, MyBot(3))
    proxy.run_once()

