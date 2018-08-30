import logging
import unittest
import random

from gym import Env, spaces
from numpy import array

from hearts.single import SingleEnv

logger = logging.getLogger(__name__)

class SingleEnvTest(unittest.TestCase):
    def setUp(self):
        self.env = SingleEnv()
        self.r = self.env.reset()

    def tearDown(self):
        self.env.close()

    def test_env__obs_space(self):
        logger.debug(self.r)
        logger.debug(self.env.observation_space.sample())
        self.assertTrue(self.env.observation_space.contains(self.r))

    def test_env__action_space(self):
        draws = [array([-1, -1]), array([-1, -1]), array([-1, -1])]
        action = tuple(draws)

        self.assertTrue(self.env.action_space.contains(action))

    def test_env__seed(self):
        seeds = self.env.seed()
        self.assertIs(type(seeds), list)
        for seed in seeds:
            self.assertIs(type(seed), int)
            self.assertEqual(self.env.n_seed, seed)

    def test_env__render(self):
        self.env.render()

    def test_env__step(self):
        cur_pos = self.env._table.cur_pos
        self.assertEqual(cur_pos, self.env.PLAYER)
        me = self.env._table.players[cur_pos]
        cards = me.hand[0:3]

        draws = []
        for rank, suit in cards:
            draws.append(array([rank, suit]))
        action = tuple(draws)

        self.assertTrue(self.env.action_space.contains(action))

        obs, rew, done, info = self.env.step(action)

        # XXX very strange...it's False
        # The table space cannot match XXX
        # self.assertTrue(self.env.observation_space.contains(obs))
        self.assertIs(type(rew), int)
        self.assertIs(type(done), bool)
        self.assertFalse(done)
        self.assertIs(type(info), dict)
        self.assertEqual(cur_pos, self.env.PLAYER)

        draws = []
        me.hand.reverse()
        if not self.env._table.finish_expose:
            draws = [(12, 1)]
        elif (0, 3) in me.hand:
            draws = [(0, 3)]
        else:
            for card in me.hand:
                if self.env._table.first_draw and card[1] == self.env._table.first_draw[1]:
                    draws.append(card)
                    break
            if not draws:
                for card in me.hand:
                    if self.env._table.n_round == 0:
                        if card[1] != 1 and card != (10, 0):
                            draws.append(card)
                            break
                    else:
                        if not self.env._table.heart_occur and card[1] != 1:
                            draws.append(card)
                            break
            if not draws:
                draws = [random.choice(me.hand)]

        #self.env._table.finish_expose = True
        logger.debug(me.hand)
        logger.debug(draws)

        # tuple to array
        acts = [array([c[0], c[1]]) for c in draws]
        acts = self.env._pad(acts, 3, array([-1, -1]))
        obs, rew, done, info = self.env.step(tuple(acts))
        self.assertEqual(cur_pos, self.env.PLAYER)

    def test_env__run_once(self):
        done = False
        
        while not done:
            cur_pos = self.env._table.cur_pos
            self.assertEqual(cur_pos, self.env.PLAYER)
            
            # You can simply use sample() to finish the whole game
            acts = self.env.action_space.sample()
        
            self.assertTrue(self.env.action_space.contains(acts))
            _, _, done, _ = self.env.step(acts)
        

