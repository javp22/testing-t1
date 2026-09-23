import sys
import pytest
from unittest.mock import MagicMock

# Inyectamos un stub para 'numpy' en sys.modules para evitar el ModuleNotFoundError
# dado que el código fuente requiere 'utils' y este a su vez requiere 'numpy'.
# Esto permite que se carguen los módulos originales sin necesidad de instalar numpy.
sys.modules['numpy'] = MagicMock()

# Ajustar el path para asegurar la importación correcta desde la ubicación del archivo
sys.path.insert(0, '/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/mahjong')

from dealer import MahjongDealer

class MockPlayer:
    def __init__(self):
        self.hand = []

def test_mahjong_dealer_initialization():
    mock_np_random = MagicMock()
    dealer = MahjongDealer(mock_np_random)
    
    assert hasattr(dealer, 'deck')
    assert mock_np_random.shuffle.called
    assert dealer.table == []

def test_shuffle():
    mock_np_random = MagicMock()
    dealer = MahjongDealer(mock_np_random)
    initial_deck = list(dealer.deck)
    
    dealer.shuffle()
    
    # Verificar que se llamó al método shuffle del mock pasando el deck
    mock_np_random.shuffle.assert_called_with(dealer.deck)
    assert len(dealer.deck) == len(initial_deck)

def test_deal_cards_normal():
    mock_np_random = MagicMock()
    dealer = MahjongDealer(mock_np_random)
    player = MockPlayer()
    num_cards = 5
    initial_deck_len = len(dealer.deck)
    
    dealer.deal_cards(player, num_cards)
    
    assert len(player.hand) == num_cards
    assert len(dealer.deck) == initial_deck_len - num_cards

def test_deal_cards_boundary_zero():
    mock_np_random = MagicMock()
    dealer = MahjongDealer(mock_np_random)
    player = MockPlayer()
    
    dealer.deal_cards(player, 0)
    
    assert len(player.hand) == 0

def test_deal_cards_exception_empty_deck():
    mock_np_random = MagicMock()
    dealer = MahjongDealer(mock_np_random)
    # Vaciar el deck para forzar el IndexError en el pop() interno
    dealer.deck = []
    player = MockPlayer()
    
    with pytest.raises(IndexError):
        dealer.deal_cards(player, 1)

def test_deal_cards_integrity():
    mock_np_random = MagicMock()
    dealer = MahjongDealer(mock_np_random)
    player = MockPlayer()
    
    # Guardar referencia al elemento que se espera extraer (el último)
    target_card = dealer.deck[-1]
    
    dealer.deal_cards(player, 1)
    
    assert player.hand[0] == target_card