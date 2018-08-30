import pandas as pd

RANK_TO_INT = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9}
INT_TO_RANK = dict([(v, k) for k, v in RANK_TO_INT.items()])

class Card:

    # Takes in strings of the format: "As", "Tc", "6d"
    def __init__(self, card_string):
        self.suit_index_dict = {"S": 0, "C": 1, "H": 2, "D": 3}
        self.val_string = "AKQJT98765432"
        value, self.suit = card_string[0], card_string[1]
        self.value = RANK_TO_INT[value]
        self.suit_index = self.suit_index_dict[self.suit]

    def __str__(self):
        return self.val_string[14 - self.value] + self.suit

    def toString(self):
        return self.val_string[14 - self.value] + self.suit

    def __repr__(self):
        return self.val_string[14 - self.value] + self.suit
    def __eq__(self, other):
        if self is None:
            return other is None
        elif other is None:
            return False
        return self.value == other.value and self.suit == other.suit

    def __hash__(self):
        return hash(self.value.__hash__()+self.suit.__hash__())

class Cards:
    def __init__(self, cards=None):
        self.index = [i for i in range(2, 15)]
        self.columns = ['S', 'H', 'D', 'C']
        self.df = pd.DataFrame(0, index=self.index, columns=self.columns)

        if cards:
            for card in cards:
                self.add_card(card)

    def add_card(self, card):
        if card:
            r = RANK_TO_INT[card[0]]
            s = card[1]
            self.df.loc[r, s] = 1

    def get_suit_count(self):
        return self.df.sum()

