from gym import spaces
table_space = spaces.Tuple([
    spaces.Discrete(13), # n_round
    spaces.Discrete(4), # start_pos
    spaces.Discrete(4), # cur_pos
    spaces.Discrete(1), # exchanged
    spaces.Discrete(1), # heart_occured
    spaces.Discrete(100), # n_games
    spaces.Tuple([ # board
        spaces.MultiDiscrete([13, 4])
    ] * 4),
    spaces.Tuple([ # first_draw
        spaces.MultiDiscrete([13, 4])
    ]),
    spaces.Tuple([ # bank
        spaces.Tuple([
            spaces.MultiDiscrete([13, 4])
        ] * 3),
    ] * 4)
])

player_space = spaces.Tuple([
    spaces.Discrete(200), # score
    spaces.Tuple([ # hand
        spaces.MultiDiscrete([13, 4])
    ] * 13),
    spaces.Tuple([ # income
        spaces.MultiDiscrete([13, 4])
    ] * 52),
] * 4)

p_space = spaces.Tuple([
    spaces.Discrete(200), # score
    spaces.Tuple([ # hand
        spaces.MultiDiscrete([13, 4])
    ] * 13),
    spaces.Tuple([ # income
        spaces.MultiDiscrete([13, 4])
    ] * 52),
])

