import pytest
import sys

# Asegurar que el directorio del archivo objetivo está en el path
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/mahjong/')

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

    def __repr__(self):
        return f"MockCard({self.name})"

class MockDealer:
    def __init__(self):
        self.table = []

@pytest.fixture
def player():
    return MahjongPlayer(player_id=42, np_random="seed")

@pytest.fixture
def dealer():
    return MockDealer()

def test_initialization_state(player):
    assert player.get_player_id() == 42
    assert player.np_random == "seed"
    assert player.hand == []
    assert player.pile == []

def test_play_card_state(player, dealer):
    c1, c2 = MockCard("A"), MockCard("B")
    player.hand = [c1, c2]
    player.play_card(dealer, c1)
    assert player.hand == [c2]
    assert dealer.table == [c1]

def test_play_card_raises_value_error(player, dealer):
    # Verifica que falla si la carta no está en la mano
    with pytest.raises(ValueError):
        player.play_card(dealer, MockCard("Z"))

def test_chow_logic(player, dealer):
    c1, c2, c3 = MockCard("1"), MockCard("2"), MockCard("3")
    # last_card debe ser el de la mesa (c3)
    dealer.table = [c1, c3]
    player.hand = [c1, c2]
    
    # Se pasa [c1, c2] para hacer chow con c3 (que es el último de la mesa)
    player.chow(dealer, [c1, c2])
    
    assert player.hand == []
    assert dealer.table == [c1] # c3 fue removido
    assert player.pile == [[c1, c2]]

def test_chow_ignores_card_not_in_hand_and_does_not_remove_last_card(player, dealer):
    c1, c2 = MockCard("A"), MockCard("B")
    dealer.table = [c1]
    player.hand = [c2]
    
    # Chow con c1 (en mesa) y c3 (no en mano)
    c3 = MockCard("C")
    player.chow(dealer, [c1, c3])
    
    assert player.hand == [c2]
    assert dealer.table == []
    assert player.pile == [[c1, c3]]

def test_gong_removes_specific_cards(player, dealer):
    c1, c2, c3 = MockCard("A"), MockCard("A"), MockCard("B")
    player.hand = [c1, c2, c3]
    player.gong(dealer, [c1, c2])
    assert player.hand == [c3]
    assert player.pile == [[c1, c2]]

def test_pong_removes_exact_matches(player, dealer):
    c1, c2, c3 = MockCard("A"), MockCard("A"), MockCard("A")
    player.hand = [c1, c2, c3]
    player.pong(dealer, [c1, c2])
    assert player.hand == [c3]
    assert player.pile == [[c1, c2]]

def test_print_hand_output(player, capsys):
    c1, c2 = MockCard("A"), MockCard("B")
    player.hand = [c1, c2]
    player.print_hand()
    captured = capsys.readouterr()
    assert captured.out == "['A', 'B']\n"

def test_print_pile_output(player, capsys):
    c1, c2 = MockCard("A"), MockCard("B")
    player.pile = [[c1], [c2]]
    player.print_pile()
    captured = capsys.readouterr()
    assert captured.out == "[['A'], ['B']]\n"

def test_empty_collections_behavior(player, dealer):
    # Verificar que los métodos no fallen con colecciones vacías
    player.gong(dealer, [])
    assert player.pile == [[]]
    player.pong(dealer, [])
    assert player.pile == [[], []]