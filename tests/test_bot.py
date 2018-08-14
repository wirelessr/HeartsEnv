import unittest
import logging

from hearts.bot import BotProxy

logger = logging.getLogger(__name__)

class HeartsBotTest(unittest.TestCase):
    def setUp(self):
        self.proxy = BotProxy()

    def tearDown(self):
        pass

    def test_bot__run_once(self):
        obs = self.proxy.run_once()

        max_score = 0
        for cur_pos in range(4):
            [score], (hand,), _ = tuple([obs[0][i]] for i in range(cur_pos*3, cur_pos*3+3))
            if score > max_score:
                max_score = score

        self.assertTrue(max_score >= 100)
