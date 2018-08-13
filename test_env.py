import unittest

from gym import Env, spaces
from hearts import HeartsEnv

class HeartsEnvTest(unittest.TestCase):
    def setUp(self):
        self.env = HeartsEnv()

    def tearDown(self):
        self.env.close()

    def test_obs_space(self):
        r = self.env.reset()
        self.assertTrue(self.env.observation_space.contains(r))

