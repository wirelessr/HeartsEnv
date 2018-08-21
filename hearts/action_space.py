import random
import logging

from numpy import array

logger = logging.getLogger(__name__)

class ActionSpace:
    def __init__(self, table, pos):
        self._table = table
        self._pos = pos

    def contains(self, x):
        if len(x) not in [1, 3]:
            logger.error('Length is %r', len(x))
            return False
        x = [(c[0], c[1]) for c in x if not all(c == (-1, -1))]
        if set(self._table.players[self._pos].hand).issuperset(set(x)):
            return True
        logger.debug('Not found')
        return False

    def sample(self):
        hand = self._table.players[self._pos].hand

        if self._table._need_exchange():
            # 3 cards
            draws = random.sample(hand, 3)
        else:
            # 1 card
            draws = []
            if (0, 3) in hand:
                draws = [(0, 3)]
            else:
                if self._table.first_draw:
                    for c in hand:
                        if c[1] == self._table.first_draw[1]:
                            draws.append(c)
                if not draws:
                    if self._table.n_round == 0:
                        for c in hand:
                            if c[1] != 1 and c != (10, 0):
                                draws.append(c)
                    elif not self._table.heart_occur:
                        for c in hand:
                            if c[1] != 1:
                                draws.append(c)
                
            if not draws:
                draws = hand

            draws = [random.choice(draws)]

        return [array([c[0], c[1]]) for c in draws]
                
