import sys
from unittest.mock import MagicMock

# Como numpy no está disponible, creamos un mock que simule el comportamiento de
# np.array() para que al convertir la lista a array y luego a lista no se pierda el contenido.
class MockNp:
    def array(self, obj):
        return list(obj)

sys.modules['numpy'] = MockNp()

import pytest
from blackjack.dealer import init_standard_deck, BlackjackDealer
from blackjack import Card

class MockPlayer:
    def __init__(self):
        self.hand = []

@pytest.fixture
def rng():
    # El código fuente original realiza:
    # 1. self.np_random.shuffle(shuffle_deck)
    # 2. idx = self.np_random.choice(len(self.deck))
    m = MagicMock()
    # Para shuffle, el mock no hace nada, lo cual es correcto pues la lista se modifica in-place
    # Para choice, devolvemos un índice válido.
    m.choice.return_value = 0
    return m

def test_init_standard_deck():
    deck = init_standard_deck()
    assert len(deck) == 52
    assert all(isinstance(c, Card) for c in deck)
    suits = {c.suit for c in deck}
    ranks = {c.rank for c in deck}
    assert len(suits) == 4
    assert len(ranks) == 13

def test_dealer_initialization(rng):
    d = BlackjackDealer(rng, num_decks=1)
    assert len(d.deck) == 52
    assert d.status == 'alive'
    assert d.score == 0

def test_dealer_multiple_decks(rng):
    d = BlackjackDealer(rng, num_decks=3)
    assert len(d.deck) == 52 * 3

def test_dealer_infinite_decks(rng):
    d = BlackjackDealer(rng, num_decks=0)
    assert len(d.deck) == 52

def test_shuffle(rng):
    d = BlackjackDealer(rng, num_decks=1)
    d.shuffle()
    assert rng.shuffle.called
    assert len(d.deck) == 52

def test_deal_card_removes_from_deck(rng):
    d = BlackjackDealer(rng, num_decks=1)
    p = MockPlayer()
    d.deal_card(p)
    assert len(d.deck) == 51
    assert len(p.hand) == 1

def test_deal_card_infinite_no_remove(rng):
    d = BlackjackDealer(rng, num_decks=0)
    p = MockPlayer()
    d.deal_card(p)
    assert len(d.deck) == 52
    assert len(p.hand) == 1