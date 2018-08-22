import unittest
import logging

from hearts.bot import BotProxy, SequentialBot

logger = logging.getLogger(__name__)

class HeartsBotTest(unittest.TestCase):
    def setUp(self):
        self.proxy = BotProxy()

    def tearDown(self):
        pass

    def test_bot__run_once(self):
        self.proxy.add_bot(0, SequentialBot(0))
        obs = self.proxy.run_once()

        self.assertTrue(obs[1][5] == 16)
