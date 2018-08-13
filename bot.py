import random

from hearts.hearts import HeartsEnv

class RandomBot():
    def __init__(self, idx):
        self.idx = idx
        pass

    def declare_action(self, player_obs, table_obs):
        action = [self.idx]

        score, hand, income = player_obs
        n_round, start_pos, cur_pos, exchaged, hearts_occur, n_game,\
                board, first_draw, bank = table_obs
        
        hand_card = [(c[0], c[1]) for c in hand if c[0] != -1 or c[1] != -1]
        board_card = [(c[0], c[1]) for c in board]

        if not exchanged and n_game % 4 != 0:
            # 3 cards
            draws = random.sample(hand, 3)
        else:
            # 1 card
            

        # draws = [array([-1, -1]), array([-1, -1]), array([-1, -1])]
        action.append(tuple(draws))
        return tuple(action)

class BotProxy:
    def __init__(self):
        self.bots = [RandomBot(i) for i in range(4)]
        self.env = HeartsEnv()

    def add_bot(self, pos, bot):
        self.bots[pos] = bot

    def run_one_game(self):
        obs = self.env.reset()
        done = False
        
        while not done:
            self.env.render()

            n_round, start_pos, cur_pos, exchaged, hearts_occur, n_game,\
                    board, first_draw, bank = obs[1]

            player_obs = tuple([obs[0][i]] for i in range(cur_pos*3, cur_pos*3+3))
            action = self.bots[cur_pos].declare_action(player_obs, obs[1])
            obs, rew, done, _ = self.env.step(action)

if __name__ == '__main__':
    proxy = BotProxy()
    proxy.run_one_game()

    
    

    
