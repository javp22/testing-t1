import pytest
import sys
import os

# Ajustar el path para asegurar la importación del módulo judger
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/blackjack/')

from judger import BlackjackJudger

class MockCard:
    def __init__(self, rank):
        self.rank = rank

class MockPlayer:
    def __init__(self, hand=None, status=None, score=0):
        self.hand = hand if hand is not None else []
        self.status = status
        self.score = score

class MockGame:
    def __init__(self):
        self.players = {}
        self.dealer = None
        self.winner = {}

def test_judge_score_basic():
    judger = BlackjackJudger(None)
    cards = [MockCard("2"), MockCard("3")]
    assert judger.judge_score(cards) == 5

def test_judge_score_ace_logic():
    judger = BlackjackJudger(None)
    # 11 + 11 = 22 -> 12
    cards = [MockCard("A"), MockCard("A")]
    assert judger.judge_score(cards) == 12
    # 10 + 11 + 11 = 32 -> 22 -> 12
    cards = [MockCard("T"), MockCard("A"), MockCard("A")]
    assert judger.judge_score(cards) == 12

def test_judge_round_alive():
    judger = BlackjackJudger(None)
    player = MockPlayer(hand=[MockCard("2"), MockCard("3")])
    status, score = judger.judge_round(player)
    assert status == "alive"
    assert score == 5

def test_judge_round_bust():
    judger = BlackjackJudger(None)
    player = MockPlayer(hand=[MockCard("K"), MockCard("K"), MockCard("2")])
    status, score = judger.judge_round(player)
    assert status == "bust"
    assert score == 22

def test_judge_game_player_bust():
    judger = BlackjackJudger(None)
    game = MockGame()
    game.players = {0: MockPlayer(status='bust')}
    game.winner = {}
    judger.judge_game(game, 0)
    assert game.winner['player0'] == -1

def test_judge_game_dealer_bust():
    judger = BlackjackJudger(None)
    game = MockGame()
    game.players = {0: MockPlayer(status='alive')}
    game.dealer = MockPlayer(status='bust')
    game.winner = {}
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 2

def test_judge_game_win():
    judger = BlackjackJudger(None)
    game = MockGame()
    game.players = {0: MockPlayer(status='alive', score=20)}
    game.dealer = MockPlayer(status='alive', score=19)
    game.winner = {}
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 2

def test_judge_game_tie():
    judger = BlackjackJudger(None)
    game = MockGame()
    game.players = {0: MockPlayer(status='alive', score=20)}
    game.dealer = MockPlayer(status='alive', score=20)
    game.winner = {}
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 1

def test_judge_game_loss_behavior():
    judger = BlackjackJudger(None)
    game = MockGame()
    game.players = {0: MockPlayer(status='alive', score=15)}
    game.dealer = MockPlayer(status='alive', score=20)
    game.winner = {}
    # El código original tiene: game.winner['player' % str(game_pointer)] = -1
    # 'player' % '0' lanza TypeError. 
    # Validamos que el código efectivamente falla al intentar ejecutar esa rama.
    with pytest.raises(TypeError):
        judger.judge_game(game, 0)