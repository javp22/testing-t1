import sys
from unittest.mock import MagicMock

# Inyectar mocks para todas las dependencias transitivas que impiden la carga del módulo
sys.modules['melding'] = MagicMock()
sys.modules['action_event'] = MagicMock()
sys.modules['scorers'] = MagicMock()

# Mockear el módulo utils antes de importar GinRummyDealer
mock_utils = MagicMock()
mock_utils.get_deck.return_value = [f"card_{i}" for i in range(52)]
sys.modules['utils'] = mock_utils

import pytest
from gin_rummy.dealer import GinRummyDealer

class MockPlayer:
    def __init__(self):
        self.hand = []
        self.populated = False

    def did_populate_hand(self):
        self.populated = True

class MockRandom:
    def shuffle(self, x):
        pass

def test_dealer_initialization():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    
    assert dealer.np_random == mock_rng
    assert dealer.discard_pile == []
    assert len(dealer.shuffled_deck) == 52
    assert len(dealer.stock_pile) == 52

def test_deal_cards_normal():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    player = MockPlayer()
    
    dealer.deal_cards(player, 5)
    
    assert len(player.hand) == 5
    assert player.populated is True
    assert len(dealer.stock_pile) == 47

def test_deal_cards_zero():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    player = MockPlayer()
    
    dealer.deal_cards(player, 0)
    
    assert len(player.hand) == 0
    assert player.populated is True
    assert len(dealer.stock_pile) == 52

def test_deal_cards_empty_stock_raises_index_error():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    player = MockPlayer()
    
    # Vaciar el stock_pile manualmente para forzar el comportamiento de pop en lista vacía
    dealer.stock_pile = []
    
    with pytest.raises(IndexError):
        dealer.deal_cards(player, 1)

def test_deal_cards_complete_deck():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    player = MockPlayer()
    
    dealer.deal_cards(player, 52)
    
    assert len(player.hand) == 52
    assert len(dealer.stock_pile) == 0
    assert player.populated is True