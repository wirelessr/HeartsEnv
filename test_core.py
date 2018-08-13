import unittest

from hearts_core import *

class HeartsCoreTest(unittest.TestCase):
    def setUp(self):
        self.table = Table()
        self.player = Player()

    def tearDown(self):
        pass

    def test_player__get_rewards__normal(self):
        self.player.income = [(0,0), (1,1), (2,2), (3,3)]
        self.assertEqual(self.player.get_rewards(), -1)

        self.player.income = [(10,0), (1,1), (2,2), (3,3)]
        self.assertEqual(self.player.get_rewards(), -14)

    def test_player__get_rewards__shoot_moon(self):
        self.player.income = [(i, 1) for i in range(13)]
        self.assertEqual(self.player.get_rewards(), -13)

        self.player.income.append((10, 0))
        self.assertEqual(self.player.get_rewards(), 26)

    def test_table__game_start__normal(self):
        self.table.game_start()
        self.assertEqual(len(self.table.players), 4)
        for player in self.table.players:
            self.assertEqual(len(player.hand), 13)
            self.assertEqual(len(player.income), 0)
            



