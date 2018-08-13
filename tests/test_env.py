import unittest

from gym import Env, spaces
from numpy import array

from ..hearts import HeartsEnv

class HeartsEnvTest(unittest.TestCase):
    def setUp(self):
        self.env = HeartsEnv()
        self.r = self.env.reset()

    def tearDown(self):
        self.env.close()

    def test_env__obs_space(self):
        self.assertTrue(self.env.observation_space.contains(self.r))

    def test_env__action_space(self):
        action = [0]
        draws = [array([-1, -1]), array([-1, -1]), array([-1, -1])]
        action.append(tuple(draws))

        self.assertTrue(self.env.action_space.contains(tuple(action)))

    def test_env__seed(self):
        seeds = self.env.seed()
        self.assertIs(type(seeds), list)
        for seed in seeds:
            self.assertIs(type(seed), int)

    def test_env__render(self):
        self.env.render()

    def test_env__step(self):
        cur_pos = self.env._table.cur_pos
        cards = self.env._table.players[cur_pos].hand[0:3]

        action = [cur_pos]
        draws = []
        for rank, suit in cards:
            draws.append(array([rank, suit]))
        action.append(tuple(draws))

        self.assertTrue(self.env.action_space.contains(tuple(action)))

        obs, rew, done, info = self.env.step(action)
        self.assertTrue(self.env.observation_space.contains(obs))
        self.assertIs(type(rew), int)
        self.assertIs(type(done), bool)
        self.assertFalse(done)
        self.assertIs(type(info), dict)
