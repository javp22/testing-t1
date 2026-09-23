import sys
import os
import pytest

# Asegurar que el directorio donde reside player.py esté en el path
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/mahjong')

from player import MahjongPlayer

class MockCard:
    def __init__(self, name):
        self.name = name
    def get_str(self):
        return self.name
    def __eq__(self, other):
        return isinstance(other, MockCard) and self.name == other.name

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

def test_play_card(player):
    dealer = MockDealer()
    card = MockCard("A")
    player.hand = [card]
    
    player.play_card(dealer, card)
    
    assert len(player.hand) == 0
    assert dealer.table == [card]

def test_play_card_value_error(player):
    dealer = MockDealer()
    card = MockCard("A")
    # Al intentar hacer .index() de un elemento que no existe en la lista, lanza ValueError
    with pytest.raises(ValueError):
        player.play_card(dealer, card)

def test_chow(player):
    dealer = MockDealer()
    card1 = MockCard("1")
    card2 = MockCard("2")
    last_card = MockCard("3")
    dealer.table = [last_card]
    player.hand = [card1, card2]
    
    # El método chow hace pop de dealer.table, requiere que haya algo en la tabla
    player.chow(dealer, [card1, card2])
    
    assert len(player.hand) == 0
    assert player.pile == [[card1, card2]]
    assert len(dealer.table) == 0

def test_gong(player):
    dealer = MockDealer()
    cards = [MockCard("1"), MockCard("1"), MockCard("1"), MockCard("1")]
    player.hand = list(cards)
    
    player.gong(dealer, cards)
    
    assert len(player.hand) == 0
    assert player.pile == [cards]

def test_pong(player):
    dealer = MockDealer()
    cards = [MockCard("5"), MockCard("5"), MockCard("5")]
    player.hand = list(cards)
    
    player.pong(dealer, cards)
    
    assert len(player.hand) == 0
    assert player.pile == [cards]

def test_print_hand(player, capsys):
    player.hand = [MockCard("A"), MockCard("B")]
    player.print_hand()
    captured = capsys.readouterr()
    assert "['A', 'B']" in captured.out

def test_print_pile(player, capsys):
    # La estructura es [[str1, str2]] para una lista de cartas dentro de la pila
    player.pile = [[MockCard("A"), MockCard("B")]]
    player.print_pile()
    captured = capsys.readouterr()
    assert "[['A', 'B']]" in captured.out