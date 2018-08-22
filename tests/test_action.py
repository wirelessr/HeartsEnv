import logging
import unittest
import random

from gym import Env, spaces
from numpy import array

from hearts.hearts_core import Table
from hearts.action_space import ActionSpace

logger = logging.getLogger(__name__)

class ActionSpaceTest(unittest.TestCase):
    def setUp(self):
        self.table = Table()
        self.table.game_start()
        self.action = ActionSpace(self.table, 0)
        self.hand = self.table.players[0].hand

    def tearDown(self):
        self.table.reset()

    def test_action__contains(self):
        for c in self.hand:
            self.assertTrue(self.action.contains([array([c[0], c[1]])]))

        hands = [array([c[0], c[1]]) for c in self.hand[0:2]]
        self.assertFalse(self.action.contains(hands))

        hands = [array([c[0], c[1]]) for c in self.hand[0:3]]
        self.assertTrue(self.action.contains(hands))

    def test_action__sample(self):
        self.table.players[0].hand = [(0, 0), (1, 1), (2, 2)]
        sample = [(c[0], c[1]) for c in self.action.sample()]
        self.assertEqual(set(self.table.players[0].hand), set(sample))
        
        self.table.exchanged = True
        self.table.finish_expose = True
        sample = [(c[0], c[1]) for c in self.action.sample()]
        self.assertEqual(len(sample), 1)
        self.assertIn(sample[0], [(0, 0), (2, 2)])
        
        self.table.players[0].hand = [(0, 3), (1, 1), (2, 2)]
        self.table.exchanged = True
        sample = [(c[0], c[1]) for c in self.action.sample()]
        self.assertEqual(len(sample), 1)
        self.assertEqual(sample[0], (0, 3))

        self.table.players[0].hand = [(0, 0), (1, 1), (2, 2)]
        self.table.first_draw = (3, 2)
        sample = [(c[0], c[1]) for c in self.action.sample()]
        self.assertEqual(len(sample), 1)
        self.assertEqual(sample[0], (2, 2))
        
