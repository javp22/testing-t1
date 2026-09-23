import pytest
import sys
from unittest.mock import MagicMock

# Ajustar path para encontrar los archivos requeridos
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/gin_rummy')

# Simular dependencias ausentes en el entorno para evitar errores de importación
sys.modules['gin_rummy'] = MagicMock()
sys.modules['utils'] = MagicMock()

# Importar el código objetivo
from dealer import GinRummyDealer
import utils

# Definir un mazo de prueba constante para las pruebas
TEST_DECK = ["C1", "C2", "C3", "C4", "C5"]

# Configurar el mock de utils para que get_deck retorne una copia nueva cada vez
utils.get_deck = lambda: TEST_DECK.copy()

class MockPlayer:
    def __init__(self):
        self.hand = []
        self.populated = False
    
    def did_populate_hand(self):
        self.populated = True

class MockRandom:
    def __init__(self):
        self.shuffle_called = False
    
    def shuffle(self, deck):
        self.shuffle_called = True

def test_dealer_initialization():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    
    assert dealer.np_random == mock_rng
    assert dealer.discard_pile == []
    assert len(dealer.shuffled_deck) == len(TEST_DECK)
    assert dealer.stock_pile == dealer.shuffled_deck
    assert dealer.stock_pile is not dealer.shuffled_deck
    assert mock_rng.shuffle_called is True

def test_deal_cards_logic():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    player = MockPlayer()
    
    num_cards = 2
    dealer.deal_cards(player, num_cards)
    
    assert len(player.hand) == num_cards
    assert len(dealer.stock_pile) == len(TEST_DECK) - num_cards
    assert player.populated is True

def test_deal_cards_zero():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    player = MockPlayer()
    
    dealer.deal_cards(player, 0)
    
    assert len(player.hand) == 0
    assert len(dealer.stock_pile) == len(TEST_DECK)
    assert player.populated is True

def test_deal_cards_exceeds_stock():
    mock_rng = MockRandom()
    dealer = GinRummyDealer(mock_rng)
    player = MockPlayer()
    
    # Intentar sacar más cartas de las disponibles (len(TEST_DECK) es 5)
    with pytest.raises(IndexError):
        dealer.deal_cards(player, 6)