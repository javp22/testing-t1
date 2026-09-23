import sys
import os
import pytest

# Asegurar que el directorio del archivo base esté en el path para que el import funcione
sys.path.insert(0, '/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/blackjack/')

from base import Card

def test_card_initialization():
    card = Card('S', 'A')
    assert card.suit == 'S'
    assert card.rank == 'A'

def test_card_equality():
    card1 = Card('H', 'K')
    card2 = Card('H', 'K')
    card3 = Card('D', '5')
    
    assert card1 == card2
    assert card1 != card3
    # En Python, si __eq__ devuelve NotImplemented, el operador != 
    # usa la comparación de identidad o invoca el __eq__ reflejado.
    # card1 != "KS" es True porque "KS" no es una instancia de Card.
    assert card1 != "KS"

def test_card_hash():
    card1 = Card('S', 'A')
    card2 = Card('S', 'A')
    card3 = Card('H', '2')
    
    assert hash(card1) == hash(card2)
    assert hash(card1) != hash(card3)

def test_card_str():
    card = Card('C', 'T')
    assert str(card) == 'TC'

def test_card_get_index():
    card = Card('D', 'J')
    assert card.get_index() == 'DJ'

def test_valid_suit_rank_constants():
    assert 'S' in Card.valid_suit
    assert 'A' in Card.valid_rank
    assert len(Card.valid_suit) == 6
    assert len(Card.valid_rank) == 13

@pytest.mark.parametrize("suit, rank", [
    ('S', 'A'),
    ('H', '2'),
    ('D', 'T'),
    ('C', 'K'),
    ('BJ', 'Q'),
    ('RJ', 'J')
])
def test_all_valid_combinations(suit, rank):
    card = Card(suit, rank)
    assert card.suit == suit
    assert card.rank == rank

def test_eq_with_non_card_type():
    card = Card('S', 'A')
    # Al no ser una instancia de Card, __eq__ devuelve NotImplemented,
    # lo que causa que la comparación directa == con otro tipo sea False.
    assert (card == 123) is False