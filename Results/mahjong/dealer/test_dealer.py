import sys
import os
import pytest

# Asegurar que el directorio del archivo fuente esté en el path de búsqueda de módulos
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/mahjong')

from dealer import MahjongDealer

class MockPlayer:
    def __init__(self):
        self.hand = []

class MockRandom:
    def shuffle(self, deck):
        # Implementación simple de shuffle: invierte la lista
        deck.reverse()

@pytest.fixture
def dealer():
    np_random = MockRandom()
    return MahjongDealer(np_random)

def test_init(dealer):
    # Verifica que el mazo se inicializa como una lista y no está vacío
    assert isinstance(dealer.deck, list)
    assert len(dealer.deck) > 0
    assert dealer.table == []

def test_shuffle(dealer):
    # La inicialización ya hace un shuffle. Creamos una copia para comparar.
    original_deck = list(dealer.deck)
    dealer.shuffle()
    # Con el MockRandom, el mazo debería estar invertido respecto a su estado previo
    assert dealer.deck == original_deck[::-1]

def test_deal_cards_normal(dealer):
    player = MockPlayer()
    num_to_deal = 5
    initial_deck_size = len(dealer.deck)
    
    dealer.deal_cards(player, num_to_deal)
    
    assert len(player.hand) == num_to_deal
    assert len(dealer.deck) == initial_deck_size - num_to_deal

def test_deal_cards_zero(dealer):
    player = MockPlayer()
    initial_deck_size = len(dealer.deck)
    dealer.deal_cards(player, 0)
    assert len(player.hand) == 0
    assert len(dealer.deck) == initial_deck_size

def test_deal_cards_all(dealer):
    player = MockPlayer()
    total_cards = len(dealer.deck)
    dealer.deal_cards(player, total_cards)
    assert len(player.hand) == total_cards
    assert len(dealer.deck) == 0

def test_deal_cards_empty_deck_exception(dealer):
    player = MockPlayer()
    total_cards = len(dealer.deck)
    # Vaciar el mazo completamente
    dealer.deal_cards(player, total_cards)
    
    # Intentar sacar una carta más de un mazo vacío debe lanzar IndexError
    with pytest.raises(IndexError):
        dealer.deal_cards(player, 1)