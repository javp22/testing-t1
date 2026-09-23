import sys
import os
import pytest

# Asegurar que el directorio del archivo fuente esté en el path de búsqueda de módulos
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/blackjack/')

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
    # En Python, el resultado de __eq__ cuando devuelve NotImplemented 
    # ante una comparación con un tipo no soportado, resulta en False al usar !=
    # y True al usar == con el objeto a la inversa, pero el operador ==
    # con un tipo distinto evalúa a False.
    assert (card1 == "HK") is False

def test_card_hash():
    card1 = Card('S', 'A')
    card2 = Card('S', 'A')
    card3 = Card('H', 'K')
    assert hash(card1) == hash(card2)
    assert hash(card1) != hash(card3)

def test_card_str():
    card = Card('C', 'T')
    assert str(card) == 'TC'

def test_card_get_index():
    card = Card('BJ', 'A')
    assert card.get_index() == 'BJA'

def test_card_valid_suit_rank_constants():
    assert len(Card.valid_suit) == 6
    assert len(Card.valid_rank) == 13
    assert 'S' in Card.valid_suit
    assert 'A' in Card.valid_rank

def test_card_inequality_with_different_type():
    card = Card('S', 'A')
    assert (card == 123) is False

def test_card_hash_uniqueness():
    seen_hashes = set()
    for s in Card.valid_suit:
        for r in Card.valid_rank:
            c = Card(s, r)
            h = hash(c)
            assert h not in seen_hashes
            seen_hashes.add(h)