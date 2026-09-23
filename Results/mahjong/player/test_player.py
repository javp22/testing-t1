import sys
import os
import pytest

# Ajustar el path para asegurar que el módulo player sea encontrado
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/mahjong')

from player import MahjongPlayer

class MockCard:
    def __init__(self, value):
        self.value = value
    def get_str(self):
        return str(self.value)
    def __eq__(self, other):
        if not isinstance(other, MockCard):
            return False
        return self.value == other.value

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
    card1 = MockCard(1)
    card2 = MockCard(2)
    player.hand = [card1, card2]
    
    player.play_card(dealer, card1)
    
    assert card1 not in player.hand
    assert card2 in player.hand
    assert dealer.table == [card1]

def test_play_card_value_error(player):
    dealer = MockDealer()
    card1 = MockCard(1)
    # Al intentar hacer .index() de una carta que no está en la mano, 
    # la lista de Python lanza ValueError
    with pytest.raises(ValueError):
        player.play_card(dealer, card1)

def test_chow(player):
    dealer = MockDealer()
    c_last = MockCard(10)
    c1 = MockCard(1)
    c2 = MockCard(2)
    dealer.table = [c_last]
    player.hand = [c1, c2]
    
    player.chow(dealer, [c1, c2])
    
    # dealer.table.pop(-1) remueve c_last
    assert len(dealer.table) == 0
    assert player.pile == [[c1, c2]]
    assert c1 not in player.hand
    assert c2 not in player.hand

def test_gong(player):
    dealer = MockDealer()
    c1, c2, c3, c4 = MockCard(1), MockCard(1), MockCard(1), MockCard(1)
    player.hand = [c1, c2, c3, c4]
    
    player.gong(dealer, [c1, c2, c3, c4])
    
    assert player.pile == [[c1, c2, c3, c4]]
    assert len(player.hand) == 0

def test_pong(player):
    dealer = MockDealer()
    c1, c2, c3 = MockCard(5), MockCard(5), MockCard(5)
    player.hand = [c1, c2, c3]
    
    player.pong(dealer, [c1, c2, c3])
    
    assert player.pile == [[c1, c2, c3]]
    assert len(player.hand) == 0

def test_print_hand(player, capsys):
    player.hand = [MockCard(1)]
    player.print_hand()
    captured = capsys.readouterr()
    assert captured.out.strip() == "['1']"

def test_print_pile(player, capsys):
    player.pile = [[MockCard(1), MockCard(2)]]
    player.print_pile()
    captured = capsys.readouterr()
    assert captured.out.strip() == "[['1', '2']]"

def test_chow_logic_branch(player):
    dealer = MockDealer()
    # last_card es la carta que se retira del dealer
    dealer.table = [MockCard(10)]
    c1 = MockCard(1)
    # Se intenta Chow con c1 y la misma carta del dealer (10)
    # El código debe ignorar c1 == last_card si se diera el caso,
    # pero aquí probamos la lógica de filtrado del if
    player.hand = [c1]
    player.chow(dealer, [c1, MockCard(10)])
    assert player.pile == [[c1, MockCard(10)]]
    assert c1 not in player.hand