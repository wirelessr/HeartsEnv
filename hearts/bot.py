import random
import logging

from numpy import array

from hearts.hearts import HeartsEnv

logger = logging.getLogger(__name__)

class BotBase:
    def __init__(self, idx):
        self.idx = idx
        pass

    def declare_action(self, player_obs, table_obs):
        raise NotImplemented()

class RandomBot(BotBase):
    def declare_action(self, player_obs, table_obs):
        action = [self.idx]

        score, (hand,), (income,) = player_obs
        n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game,\
            finish_expose, heart_exposed, board, (first_draw,), bank = table_obs
        
        hand_card = [c for c in hand if c[0] != -1 or c[1] != -1]
        board_card = [c for c in board]

        if not exchanged and n_game % 4 != 0:
            # 3 cards
            draws = random.sample(hand, 3)
        elif not finish_expose:
            draws = [array([12, 1]), array([-1, -1]), array([-1, -1])]
        else:
            # 1 card
            if self.idx == start_pos and n_round == 0:
                draws = [array([0, 3])]
            else:
                for card in hand_card:
                    if card[1] == first_draw[1]:
                        draws = [card]
                        break
                else:
                    for card in hand_card:
                        (rank, suit) = (card[0], card[1])
                        if n_round == 0:
                            if suit != 1 and not all(card == (10, 0)):
                                draws = [card]
                                break
                        elif not hearts_occur and suit != 1:
                            draws = [card]
                            break
                    else:
                        draws = [random.choice(hand_card)]

            draws += [array([-1, -1]), array([-1, -1])]

        action.append(tuple(draws))
        return tuple(action)

class SequentialBot(BotBase):
    def declare_action(self, player_obs, table_obs):
        action = [self.idx]

        score, (hand,), (income,) = player_obs
        n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game,\
            finish_expose, heart_exposed, board, (first_draw,), bank = table_obs
        
        hand_card = sorted([c for c in hand if c[0] != -1 or c[1] != -1],\
                key=lambda x: (x[1], x[0]), reverse=True)
        board_card = [c for c in board]

        if not exchanged and n_game % 4 != 0:
            # 3 cards
            draws = random.sample(hand, 3)
        elif not finish_expose:
            draws = [array([12, 1]), array([-1, -1]), array([-1, -1])]
        else:
            # 1 card
            if self.idx == start_pos and n_round == 0:
                draws = [array([0, 3])]
            else:
                for card in hand_card:
                    if card[1] == first_draw[1]:
                        draws = [card]
                        break
                else:
                    for card in hand_card:
                        (rank, suit) = (card[0], card[1])
                        if n_round == 0:
                            if suit != 1 and not all(card == (10, 0)):
                                draws = [card]
                                break
                        elif not hearts_occur and suit != 1:
                            draws = [card]
                            break
                    else:
                        draws = [random.choice(hand_card)]

            draws += [array([-1, -1]), array([-1, -1])]

        action.append(tuple(draws))
        return tuple(action)

class BotProxy:
    def __init__(self, render_delay=None, mode='human'):
        self.bots = [RandomBot(i) for i in range(4)]
        self.env = HeartsEnv(render_delay)
        self.mode = mode

    def add_bot(self, pos, bot):
        self.bots[pos] = bot

    def run_once(self):
        obs = self.env.reset()
        done = False
        
        while not done:
            self.env.render(self.mode)

            n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game,\
            finish_expose, heart_exposed, board, (first_draw,), bank = obs[1]

            player_obs = tuple([obs[0][i]] for i in range(cur_pos*3, cur_pos*3+3))
            action = self.bots[cur_pos].declare_action(player_obs, obs[1])
            obs, rew, done, _ = self.env.step(action)

        self.env.render(self.mode)
        return obs

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

            return max_target

        return card

    def to_array(self):
        t = np.array([])
        for p in self.players:
            t = np.append(t, p.to_array())
        return np.append(t, self.table.to_array())

