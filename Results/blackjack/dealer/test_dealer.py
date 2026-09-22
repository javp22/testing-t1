import sys
import os
from unittest.mock import MagicMock

# El problema es que init_standard_deck depende de la clase Card.
# Al mockear 'numpy', el código corre, pero 'init_standard_deck' falla si no encuentra 'Card'.
# Debemos asegurar que 'blackjack' esté en el path y que Card sea accesible.

sys.path.insert(0, '/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/blackjack')
sys.modules['numpy'] = MagicMock()

# Importamos directamente del código fuente
from blackjack import Card
from dealer import init_standard_deck, BlackjackDealer

class MockPlayer:
    def __init__(self):
        self.hand = []

def test_init_standard_deck():
    deck = init_standard_deck()
    assert len(deck) == 52
    assert all(isinstance(card, Card) for card in deck)

def test_blackjack_dealer_initialization():
    mock_rng = MagicMock()
    dealer = BlackjackDealer(mock_rng, num_decks=1)
    # init_standard_deck() crea 52 cartas, por lo que deck no debe estar vacío
    assert len(dealer.deck) == 52
    assert dealer.status == 'alive'
    assert dealer.score == 0
    assert mock_rng.shuffle.called

def test_blackjack_dealer_multiple_decks():
    mock_rng = MagicMock()
    dealer = BlackjackDealer(mock_rng, num_decks=2)
    # 52 * 2 = 104
    assert len(dealer.deck) == 104

def test_blackjack_dealer_infinite_decks():
    mock_rng = MagicMock()
    dealer = BlackjackDealer(mock_rng, num_decks=0)
    assert len(dealer.deck) == 52

def test_shuffle():
    mock_rng = MagicMock()
    dealer = BlackjackDealer(mock_rng, num_decks=1)
    initial_deck = list(dealer.deck)
    dealer.shuffle()
    assert len(dealer.deck) == 52
    assert mock_rng.shuffle.called

def test_deal_card_standard():
    mock_rng = MagicMock()
    # Mocking choice(n) para devolver un índice válido
    mock_rng.choice.return_value = 0
    
    dealer = BlackjackDealer(mock_rng, num_decks=1)
    player = MockPlayer()
    
    dealer.deal_card(player)
    
    assert len(player.hand) == 1
    assert len(dealer.deck) == 51

def test_deal_card_infinite_decks():
    mock_rng = MagicMock()
    mock_rng.choice.return_value = 0
    
    dealer = BlackjackDealer(mock_rng, num_decks=0)
    player = MockPlayer()
    
    dealer.deal_card(player)
    
    assert len(player.hand) == 1
    # Con num_decks=0, el código salta el .pop()
    assert len(dealer.deck) == 52