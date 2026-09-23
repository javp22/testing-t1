import pytest
import sys
from unittest.mock import MagicMock, patch

# Configuración de path para importar el módulo bajo prueba
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/mahjong')
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1')

# Se mockea init_deck para devolver una lista nueva en cada llamada, 
# evitando que los tests compartan el estado de la lista.
def create_mock_deck():
    return ["c1", "c2", "c3", "c4", "c5"]

mock_utils = MagicMock()
mock_utils.init_deck = create_mock_deck

with patch.dict(sys.modules, {'utils': mock_utils}):
    from dealer import MahjongDealer

class MockPlayer:
    def __init__(self):
        self.hand = []

@pytest.fixture
def mock_random():
    return MagicMock()

def test_mahjong_dealer_initialization(mock_random):
    dealer = MahjongDealer(mock_random)
    
    assert len(dealer.deck) == 5
    assert mock_random.shuffle.called
    assert dealer.table == []

def test_mahjong_dealer_shuffle(mock_random):
    dealer = MahjongDealer(mock_random)
    mock_random.shuffle.reset_mock()
    dealer.shuffle()
    assert mock_random.shuffle.called
    mock_random.shuffle.assert_called_with(dealer.deck)

def test_deal_cards_normal(mock_random):
    dealer = MahjongDealer(mock_random)
    player = MockPlayer()
    
    dealer.deal_cards(player, 2)
    
    assert len(player.hand) == 2
    assert len(dealer.deck) == 3

def test_deal_cards_zero(mock_random):
    dealer = MahjongDealer(mock_random)
    player = MockPlayer()
    
    dealer.deal_cards(player, 0)
    
    # El deck debe mantener sus 5 cartas iniciales
    assert len(player.hand) == 0
    assert len(dealer.deck) == 5

def test_deal_cards_empty_deck_raises_exception(mock_random):
    dealer = MahjongDealer(mock_random)
    player = MockPlayer()
    
    # Vaciar el deck manualmente
    dealer.deck = []
        
    with pytest.raises(IndexError):
        dealer.deal_cards(player, 1)

def test_deal_cards_exceeding_deck_raises_exception(mock_random):
    dealer = MahjongDealer(mock_random)
    player = MockPlayer()
    
    # Intentar sacar 6 cartas de un deck inicial de 5
    with pytest.raises(IndexError):
        dealer.deal_cards(player, 6)