import pytest
from judger import BlackjackJudger

class MockCard:
    def __init__(self, rank):
        self.rank = rank

class MockPlayer:
    def __init__(self, hand, status=None, score=None):
        self.hand = hand
        self.status = status
        self.score = score

class MockGame:
    def __init__(self, players, dealer):
        self.players = players
        self.dealer = dealer
        self.winner = {}

def test_judge_score():
    judger = BlackjackJudger(None)
    
    # Normal case
    cards = [MockCard("2"), MockCard("3")]
    assert judger.judge_score(cards) == 5
    
    # Ace as 11
    cards = [MockCard("A"), MockCard("5")]
    assert judger.judge_score(cards) == 16
    
    # Ace adjustment (bust avoided)
    cards = [MockCard("A"), MockCard("K"), MockCard("2")]
    assert judger.judge_score(cards) == 13
    
    # Multiple aces
    cards = [MockCard("A"), MockCard("A"), MockCard("A")]
    assert judger.judge_score(cards) == 13 # 11+1+1

def test_judge_round():
    judger = BlackjackJudger(None)
    
    # Player alive
    player = MockPlayer([MockCard("K"), MockCard("5")])
    status, score = judger.judge_round(player)
    assert status == "alive"
    assert score == 15
    
    # Player bust
    player = MockPlayer([MockCard("K"), MockCard("Q"), MockCard("5")])
    status, score = judger.judge_round(player)
    assert status == "bust"
    assert score == 25

def test_judge_game():
    judger = BlackjackJudger(None)
    
    # Case: Player bust
    player = MockPlayer([], status='bust')
    game = MockGame([player], None)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == -1
    
    # Case: Dealer bust (player not bust)
    dealer = MockPlayer([], status='bust')
    player = MockPlayer([], status='alive')
    game = MockGame([player], dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 2
    
    # Case: Player score > Dealer score
    dealer = MockPlayer([], status='alive', score=15)
    player = MockPlayer([], status='alive', score=18)
    game = MockGame([player], dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 2
    
    # Case: Player score < Dealer score
    dealer = MockPlayer([], status='alive', score=20)
    player = MockPlayer([], status='alive', score=18)
    game = MockGame([player], dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == -1
    
    # Case: Tie
    dealer = MockPlayer([], status='alive', score=19)
    player = MockPlayer([], status='alive', score=19)
    game = MockGame([player], dealer)
    judger.judge_game(game, 0)
    assert game.winner['player0'] == 1