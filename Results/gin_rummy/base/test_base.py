import sys
import os
import pytest

# Asegurar que el directorio del archivo base esté en el path para la importación
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/gin_rummy/')

from base import Card

def test_card_initialization():
    card = Card('S', 'A')
    assert card.suit == 'S'
    assert card.rank == 'A'

def test_card_eq_same():
    card1 = Card('H', 'K')
    card2 = Card('H', 'K')
    assert card1 == card2

def test_card_eq_different_suit():
    card1 = Card('H', 'K')
    card2 = Card('D', 'K')
    assert card1 != card2

def test_card_eq_different_rank():
    card1 = Card('H', 'K')
    card2 = Card('H', 'Q')
    assert card1 != card2

def test_card_eq_different_type():
    card = Card('S', '7')
    # Comprobación de que __eq__ devuelve NotImplemented cuando el tipo no es Card
    assert (card == "7S") is False

def test_card_hash():
    card1 = Card('S', 'A')
    card2 = Card('S', 'A')
    assert hash(card1) == hash(card2)
    
    card3 = Card('H', '2')
    assert hash(card1) != hash(card3)

def test_card_str():
    card = Card('D', '9')
    assert str(card) == "9D"

def test_card_get_index():
    card = Card('C', 'T')
    assert card.get_index() == "CT"

def test_card_valid_suit_and_rank_static():
    assert 'BJ' in Card.valid_suit
    assert 'RJ' in Card.valid_suit
    assert 'A' in Card.valid_rank
    assert 'K' in Card.valid_rank

def test_hash_calculation_logic():
    # Suit index 0 (S), Rank index 0 (A) -> 0 + 100*0 = 0
    card = Card('S', 'A')
    assert hash(card) == 0
    
    # Suit index 1 (H), Rank index 1 (2) -> 1 + 100*1 = 101
    card2 = Card('H', '2')
    assert hash(card2) == 101

def test_joker_hash():
    # Suit index 4 (BJ), Rank index 0 (A) -> 0 + 100*4 = 400
    card = Card('BJ', 'A')
    assert hash(card) == 400