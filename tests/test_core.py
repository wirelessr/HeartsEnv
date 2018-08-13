import unittest

from ..hearts_core import *

class HeartsCoreTest(unittest.TestCase):
    def setUp(self):
        self.table = Table()
        self.player = Player()

    def tearDown(self):
        self.table.reset()
        pass

    def _helper(self, func):
        for i, player in enumerate(self.table.players):
            func(i, player)


    def _deal(self):
        def _dealer(i, player):
            player.hand = [(r, i) for r in range(13)]
            
        self._helper(_dealer)

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
            
    def test_table__render__normal(self):
        self.table.render()
        self.table.game_start()
        self.table.render()

    def test_table__step__failed(self):
        self._deal()

        with self.assertRaises(TurnError):
            self.table.step((4, self.table.players[0].hand[0:1]))

        with self.assertRaises(DrawError):
            self.table.step((0, [(-1, -1)]))

        with self.assertRaises(DrawMoreThanOneError):
            self.table.step((0, self.table.players[0].hand[0:2]))

        self.table.n_games = 1
        with self.assertRaises(DrawLessThanThreeError):
            self.table.step((0, self.table.players[0].hand[0:2]))


    def test_table__step__exchange(self):
        def _exchange(i, player):
            self.table.step((i, player.hand[0:3]))

        def _verify_ex(i, player):
            self.assertEqual(len(player.hand), 13)
            own = 0
            rcv = 0
            for rank, suit in player.hand:
                if suit == i:
                    own += 1
                elif self.table.n_games % 4 == 1:
                    if suit == (i + 3) % 4:
                        rcv += 1
                elif self.table.n_games % 4 == 2:
                    if suit == (i + 1) % 4:
                        rcv += 1
                elif self.table.n_games % 4 == 3:
                    if suit == (i + 2) % 4:
                        rcv += 1
            if self.table.n_games % 4 != 0:
                self.assertEqual(own, 10)
                self.assertEqual(rcv, 3)
            else:
                raise Exception('Reach here')
            
        # Exchange case except 4
        for i in range(1, 8):
            self.table.reset()
            self.table.n_games = i
            self._deal()

            if i % 4 != 0:
                self._helper(_exchange)
                self._helper(_verify_ex)

        # No need to exchange
        self.table.reset()
        self.table.n_games = 8
        self._deal()
        with self.assertRaises(DrawMoreThanOneError):
            self.table.step((0, self.table.players[0].hand[0:3]))




        



