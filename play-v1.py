import random
from numpy import array
from hearts.bot import BotProxy, BotBase

class MyBot(BotBase):
    def declare_action(self, player_obs, table_obs):
        action = [self.idx]

        score, (hand,), (income,) = player_obs
        n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game, \
        board, (first_draw,), bank = table_obs

        hand_card = sorted([c for c in hand if c[0] != -1 or c[1] != -1], \
                           key=lambda x: (x[1], x[0]), reverse=True)
        board_card = [c for c in board]

        if not exchanged and n_game % 4 != 0:
            # 3 cards
            draws = random.sample(hand, 3)
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
                        if not hearts_occur and (rank, suit) != (10, 0) and suit != 1:
                            draws = [card]
                            break
                    else:
                        draws = [random.choice(hand_card)]

            draws += [array([-1, -1]), array([-1, -1])]

        action.append(tuple(draws))
        return tuple(action)

if __name__ == '__main__':
    proxy = BotProxy(2)
    proxy.add_bot(3, MyBot(3))
    proxy.run_once()

