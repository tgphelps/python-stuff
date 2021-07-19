
import time
from typing import Set, Tuple, List

from log import log
from Shoe import Shoe
from Dealer import Dealer
from Player import Player

# This should be even, so all wins and losses are integers.
BET = 2

default_rules = {
    'num_decks': 6,
    'hit_s17': 1,
    'das_allowed': 1,
    'max_split_hands': 4,
    'max_split_aces': 2,
    'can_hit_split_aces': 0,
    'surrender': 0
    }


class Game:
    def __init__(self,
                 players=1,
                 rules=default_rules,
                 strategy={},
                 penetration=0.25,
                 repeatable=False,
                 verbose=False) -> None:
        self.verbose = verbose
        self.num_players = players
        self.players: List[Player] = []
        self.strategy: Set[Tuple[str, int, int]] = strategy
        self.rules = rules
        self.num_decks = rules['num_decks']
        self.shuffle_point = int(self.num_decks * 52 * penetration)
        self.st = Statistics()
        self.shoe = Shoe(self.num_decks, repeatable=repeatable)

        log(f"house rules: {rules}")
        self.hit_s17 = rules['hit_s17']

        log("shuffle")
        self.shoe.shuffle()
        log("new dealer")
        self.dealer = Dealer(self.shoe, hit_s17=self.hit_s17,
                             verbose=self.verbose)
        for i in range(self.num_players):
            log(f"new player: {i + 1}")
            p = Player(self.shoe, self.strategy, self.rules, self.verbose,
                       bet_amount=BET, seat=i+1)
            self.players.append(p)

    def play_round(self) -> None:
        """
        Deal hands to each player and the dealer.
        If the dealer has a BJ, settle all hands now.
        Otherwise, play each player hand, and then the dealer hand.
        Collect data on win/loss/push.
        """
        if self.shoe.remaining() < self.shuffle_point:
            log("shuffle")
            self.shoe.shuffle()

        # Deal player hands
        for p in self.players:
            self.st.hands_played += 1
            p.get_hand()
            log(f"player {p.seat}  hand: {p.hands[0]}")
            if self.verbose:
                print(f"Player: {p.hands[0]}")
            if p.hands[0].blackjack:
                log("player blackjack")
                if self.verbose:
                    print(f"Player BJ")

        self.dealer.get_hand()
        if self.dealer.hand.blackjack:
            log("dealer blackjack")
            if self.verbose:
                print("Dealer BJ")
            # No need to play the players' hands. They will all lose
            # unless they have a blackjack also.
        else:
            for p in self.players:
                log(f"player {p.seat}")
                p.play_hands(self.dealer.up_card())

            log(f"dealer: {self.dealer.hand}")
            # log("play dealer hand")
            self.dealer.play_hand()

        self.update_stats()

        for p in self.players:
            # This clears out hands just played.
            p.end_round()
        self.st.rounds_played += 1

    def update_stats(self) -> None:
        "Determine the result of each player hand. Compute wins and losses."
        log("update stats HERE --------------")
        dlr = self.dealer.hand.value
        dbj = self.dealer.hand.blackjack
        dbust = self.dealer.hand.busted
        log(f"dealer has {dlr}")
        if self.verbose:
            print('\nRESULTS')
        for p in self.players:
            for x in enumerate(p.hands):
                h = x[1]
                log(f"p{p.seat} hand {x[0]+1}: {h.value}")
                if self.verbose:
                    print(f"hand {x[0]+1}: {h.value}")
                if h.obsolete:
                    if self.verbose:
                        print('obsolete')
                    log("hand is obsolete")
                    # Hand has been split into two. Nothing to do.
                    continue
                self.st.total_bet += h.bet_amount
                if h.blackjack:
                    if not dbj:
                        self.st.blackjacks_won += 1
                        win = int(1.5 * h.bet_amount)
                        log(f"WIN: blackjack: {win}")
                        if self.verbose:
                            print(f'BJ: WIN {win}')
                        self.st.total_won += win
                        # XXX: Why is this never triggered?
                        # Answer: Because split hands can't get BJs
                        if len(p.hands) > 1:
                            print(f"hands = {len(p.hands)}")
                        continue
                if dbj:
                    if h.blackjack:
                        log("PUSH: blackjacks")
                        if self.verbose:
                            print('BJ: PUSH')
                        self.st.total_push += h.bet_amount
                    else:
                        log(f"LOSS. Dealer BJ: {h.bet_amount}")
                        if self.verbose:
                            print(f'LOSE to dealer BJ. LOSE {h.bet_amount}.')
                        self.st.total_lost += h.bet_amount
                else:  # NO BJs
                    if h.busted:
                        log(f"LOSS - busted: {h.bet_amount}")
                        if self.verbose:
                            print(f'BUST: LOSE {h.bet_amount}')
                        self.st.total_lost += h.bet_amount
                    elif h.surrendered:
                        loss = h.bet_amount // 2
                        log(f"SURRENDER: LOSE {loss}")
                        if self.verbose:
                            print(f'SURRENDER: LOSE {loss}')
                        self.st.total_lost  += loss
                        self.st.total_surrenders += 1 # XXX Assumes bet = 2 !
                    elif dbust:
                        log(f"WIN - dealer bust: {h.bet_amount}")
                        if self.verbose:
                            print(f'Dealer bust: WIN {h.bet_amount}')
                        self.st.total_won += h.bet_amount
                    elif dlr > h.value:
                        log(f"LOSS: {h.bet_amount}")
                        if self.verbose:
                            print(f'LOSE {h.bet_amount}')
                        self.st.total_lost += h.bet_amount
                    elif h.value > dlr:
                        log(f"WIN: {h.bet_amount}")
                        if self.verbose:
                            print(f'WIN {h.bet_amount}')
                        self.st.total_won += h.bet_amount
                    else:
                        log("PUSH")
                        if self.verbose:
                            print('PUSH result 0')
                        self.st.total_push += h.bet_amount
        log("                  --------------")

        # if self.dealer.hand.blackjack:
        #     self.st.dealer_blackjacks += 1

    def write_stats(self, fname: str, strategy_name: str) -> None:
        "Append stats to the stats file"
        log("writing stats")
        with open(fname, 'at') as f:
            print("time", time.asctime(), file=f)
            print("strategy", strategy_name, file=f)
            print("rounds_played", self.st.rounds_played, file=f)
            print("hands_played", self.st.hands_played, file=f)
            print("total_bet", self.st.total_bet, file=f)
            print("total_won", self.st.total_won, file=f)
            print("total_lost", self.st.total_lost, file=f)
            print("total_push", self.st.total_push, file=f)
            # print("dealer_bjs", self.st.dealer_blackjacks, file=f)
            print("blackjacks_won", self.st.blackjacks_won, file=f)
            gain = 100 * (self.st.total_won - self.st.total_lost) \
                / self.st.total_bet
            print(f"%win: {gain:5.4}", file=f)
            print("-" * 20, file=f)
            # This assertion assumes a BJ pays 3-2.
            assert self.st.total_won + self.st.total_lost + \
                self.st.total_push - self.st.blackjacks_won + \
                self.st.total_surrenders == \
                self.st.total_bet


class Statistics():
    "Just a struct to hold the data we want to accumulate."
    def __init__(self) -> None:
        self.rounds_played = 0
        self.hands_played = 0
        # self.dealer_blackjacks = 0
        self.blackjacks_won = 0
        self.total_bet = 0
        self.total_won = 0
        self.total_lost = 0
        self.total_push = 0
        self.total_surrenders = 0
