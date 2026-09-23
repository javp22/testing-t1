import sys
from unittest.mock import MagicMock

# Configuramos numpy como mock ANTES de importar los módulos del proyecto
mock_numpy = MagicMock()
sys.modules['numpy'] = mock_numpy

# Ajustamos el path para asegurar que la estructura sea localizable
# El directorio base es Public_Proyects, donde blackjack es un paquete
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects')

# Importaciones correctas según la jerarquía del proyecto
from blackjack import Card
from blackjack.dealer import init_standard_deck, BlackjackDealer

class MockPlayer:
    def __init__(self):
        self.hand = []

def test_init_standard_deck():
    deck = init_standard_deck()
    assert len(deck) == 52
    assert isinstance(deck[0], Card)
    
    suits = {card.suit for card in deck}
    ranks = {card.rank for card in deck}
    assert suits == {'S', 'H', 'D', 'C'}
    assert ranks == {'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K'}

def test_blackjack_dealer_init():
    rng = MagicMock()
    # Para que np.array(self.deck) devuelva algo real en el mock, 
    # configuramos el mock para retornar la lista inalterada
    mock_numpy.array = lambda x: x
    
    dealer = BlackjackDealer(rng, num_decks=1)
    assert len(dealer.deck) == 52
    assert dealer.status == 'alive'
    assert dealer.score == 0

def test_blackjack_dealer_multiple_decks():
    rng = MagicMock()
    mock_numpy.array = lambda x: x
    num_decks = 2
    dealer = BlackjackDealer(rng, num_decks=num_decks)
    assert len(dealer.deck) == 52 * num_decks

def test_deal_card():
    rng = MagicMock()
    mock_numpy.array = lambda x: x
    rng.choice.return_value = 0
    dealer = BlackjackDealer(rng, num_decks=1)
    player = MockPlayer()
    
    initial_len = len(dealer.deck)
    dealer.deal_card(player)
    
    assert len(dealer.deck) == initial_len - 1
    assert len(player.hand) == 1
    assert isinstance(player.hand[0], Card)

def test_deal_card_infinite_deck():
    rng = MagicMock()
    mock_numpy.array = lambda x: x
    rng.choice.return_value = 0
    dealer = BlackjackDealer(rng, num_decks=0)
    player = MockPlayer()
    
    dealer.deal_card(player)
    assert len(dealer.deck) == 52
    assert len(player.hand) == 1