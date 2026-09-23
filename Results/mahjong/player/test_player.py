import sys
import os
import pytest

# Asegurar que el path incluya el directorio del archivo objetivo
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/mahjong')

from player import MahjongPlayer

class MockCard:
    def __init__(self, name):
        self.name = name

    def get_str(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, MockCard):
            return False
        return self.name == other.name

class MockDealer:
    def __init__(self):
        self.table = []

@pytest.fixture
def player():
    return MahjongPlayer(player_id=1, np_random=None)

def test_init(player):
    assert player.get_player_id() == 1
    assert player.hand == []
    assert player.pile == []

def test_print_hand(player, capsys):
    player.hand = [MockCard("1m")]
    player.print_hand()
    captured = capsys.readouterr()
    assert captured.out.strip() == "['1m']"

def test_print_pile(player, capsys):
    player.pile = [[MockCard("1m"), MockCard("2m")]]
    player.print_pile()
    captured = capsys.readouterr()
    assert captured.out.strip() == "[['1m', '2m']]"

def test_play_card(player):
    dealer = MockDealer()
    card = MockCard("1m")
    player.hand = [card, MockCard("2m")]
    
    player.play_card(dealer, card)
    
    assert card not in player.hand
    assert len(player.hand) == 1
    assert dealer.table == [card]

def test_play_card_value_error(player):
    dealer = MockDealer()
    with pytest.raises(ValueError):
        player.play_card(dealer, MockCard("NonExistent"))

def test_chow(player):
    dealer = MockDealer()
    dealer.table = [MockCard("4m"), MockCard("5m")] # last is 5m
    cards = [MockCard("2m"), MockCard("3m")]
    player.hand = [MockCard("2m"), MockCard("3m"), MockCard("9m")]
    
    player.chow(dealer, cards)
    
    assert MockCard("9m") in player.hand
    assert len(player.hand) == 1
    assert player.pile == [cards]
    assert dealer.table == [MockCard("4m")]

def test_gong(player):
    dealer = MockDealer()
    cards = [MockCard("1m"), MockCard("1m"), MockCard("1m")]
    player.hand = [MockCard("1m"), MockCard("1m"), MockCard("1m"), MockCard("2m")]
    
    player.gong(dealer, cards)
    
    assert MockCard("2m") in player.hand
    assert player.pile == [cards]

def test_pong(player):
    dealer = MockDealer()
    cards = [MockCard("5s"), MockCard("5s")]
    player.hand = [MockCard("5s"), MockCard("5s"), MockCard("8z")]
    
    player.pong(dealer, cards)
    
    assert MockCard("8z") in player.hand
    assert player.pile == [cards]

def test_chow_logic_branch(player):
    # Prueba rama if card != last_card
    dealer = MockDealer()
    dealer.table = [MockCard("1m")] # last_card
    # Intentar hacer chow con la carta que está en la mesa (debería fallar al añadir a mano)
    cards = [MockCard("1m"), MockCard("2m")]
    player.hand = [MockCard("2m")]
    
    player.chow(dealer, cards)
    
    assert player.pile == [cards]
    assert player.hand == []