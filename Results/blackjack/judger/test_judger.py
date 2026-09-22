import pytest
import sys

# Asegurar que el directorio del archivo fuente esté en el path
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/blackjack/')

from judger import BlackjackJudger

class MockCard:
    def __init__(self, rank):
        self.rank = rank

class MockPlayer:
    def __init__(self, hand=None, score=0, status='alive'):
        self.hand = hand if hand is not None else []
        self.score = score
        self.status = status

class MockGame:
    def __init__(self, player, dealer):
        self.players = {0: player}
        self.dealer = dealer
        self.winner = {}

def test_judge_score_boundary_21():
    judger = BlackjackJudger(None)
    # K(10) + A(11) = 21
    cards = [MockCard("K"), MockCard("A")]
    assert judger.judge_score(cards) == 21

def test_judge_score_boundary_22_with_ace():
    judger = BlackjackJudger(None)
    # K(10) + K(10) + A(11) = 31 -> 21
    cards = [MockCard("K"), MockCard("K"), MockCard("A")]
    assert judger.judge_score(cards) == 21

def test_judge_score_complex_aces():
    judger = BlackjackJudger(None)
    # A(11) + A(11) + A(11) + A(11) = 44 -> 14
    cards = [MockCard("A"), MockCard("A"), MockCard("A"), MockCard("A")]
    assert judger.judge_score(cards) == 14

def test_judge_round_exactly_21():
    judger = BlackjackJudger(None)
    player = MockPlayer(hand=[MockCard("T"), MockCard("A")])
    status, score = judger.judge_round(player)
    assert status == "alive"
    assert score == 21

def test_judge_round_22_bust():
    judger = BlackjackJudger(None)
    player = MockPlayer(hand=[MockCard("T"), MockCard("T"), MockCard("2")])
    status, score = judger.judge_round(player)
    assert status == "bust"
    assert score == 22

def test_judge_game_player_bust_dealer_not():
    judger = BlackjackJudger(None)
    player = MockPlayer(status='bust', score=25)
    dealer = MockPlayer(status='alive', score=18)
    game = MockGame(player, dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == -1

def test_judge_game_player_bust_dealer_bust():
    judger = BlackjackJudger(None)
    player = MockPlayer(status='bust', score=25)
    dealer = MockPlayer(status='bust', score=22)
    game = MockGame(player, dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == -1

def test_judge_game_dealer_bust_player_alive():
    judger = BlackjackJudger(None)
    player = MockPlayer(status='alive', score=20)
    dealer = MockPlayer(status='bust', score=22)
    game = MockGame(player, dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 2

def test_judge_game_score_greater():
    judger = BlackjackJudger(None)
    player = MockPlayer(status='alive', score=20)
    dealer = MockPlayer(status='alive', score=19)
    game = MockGame(player, dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 2

def test_judge_game_score_less():
    judger = BlackjackJudger(None)
    player = MockPlayer(status='alive', score=17)
    dealer = MockPlayer(status='alive', score=18)
    game = MockGame(player, dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == -1

def test_judge_game_score_tie():
    judger = BlackjackJudger(None)
    player = MockPlayer(status='alive', score=18)
    dealer = MockPlayer(status='alive', score=18)
    game = MockGame(player, dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 1