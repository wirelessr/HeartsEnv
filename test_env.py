from gym import Env, spaces

from hearts import HeartsEnv
from part_1 import *
h = HeartsEnv()
h.reset()

class TestEnv(Env):
    def __init__(self):
        self.observation_space = spaces.Discrete(10)
        self.action_space = spaces.Discrete(2)

    def reset(self):
        return 100

t = TestEnv()
r = h.reset()

print('p',p_space.contains(r[0][0]))

print('ps',player_space.contains(r[0]))

print('ts',table_space.contains(r[1]))

print('os',h.observation_space.contains(r))
