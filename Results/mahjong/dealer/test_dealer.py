import sys
import os
import pytest
from unittest.mock import MagicMock

# Ajuste necesario para localizar el archivo dealer.py dado que el ejecutor 
# busca en una ruta específica que puede no estar en el PYTHONPATH
sys.path.append("/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/mahjong")

from dealer import MahjongDealer

class MockPlayer:
    def __init__(self):
        self.hand = []

def test_mahjong_dealer_initialization():
    # Inicialización con un objeto que soporte el método shuffle
    np_random = MagicMock()
    
    dealer = MahjongDealer(np_random)
    
    # Validaciones según estructura de MahjongDealer
    assert dealer.deck is not None
    assert isinstance(dealer.table, list)
    assert np_random.shuffle.called
    assert dealer.table == []

def test_shuffle():
    np_random = MagicMock()
    dealer = MahjongDealer(np_random)
    
    # El método shuffle delega la operación a np_random.shuffle
    dealer.shuffle()
    
    # Verificar llamada con el deck actual
    np_random.shuffle.assert_called_with(dealer.deck)

def test_deal_cards_normal():
    np_random = MagicMock()
    dealer = MahjongDealer(np_random)
    player = MockPlayer()
    
    initial_count = len(dealer.deck)
    num_to_deal = 3
    
    dealer.deal_cards(player, num_to_deal)
    
    # Verificar que las cartas fueron movidas del deck a la mano del jugador
    assert len(player.hand) == num_to_deal
    assert len(dealer.deck) == initial_count - num_to_deal

def test_deal_cards_zero():
    np_random = MagicMock()
    dealer = MahjongDealer(np_random)
    player = MockPlayer()
    
    initial_count = len(dealer.deck)
    dealer.deal_cards(player, 0)
    
    # No debe haber cambios
    assert len(player.hand) == 0
    assert len(dealer.deck) == initial_count

def test_deal_cards_index_error():
    np_random = MagicMock()
    dealer = MahjongDealer(np_random)
    player = MockPlayer()
    
    # Intentar sacar más cartas de las existentes disparará IndexError en pop()
    total_cards = len(dealer.deck)
    with pytest.raises(IndexError):
        dealer.deal_cards(player, total_cards + 1)