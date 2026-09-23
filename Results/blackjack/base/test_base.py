import sys
import os
import pytest

# Asegurar que el directorio del archivo base esté en el path de búsqueda
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/blackjack')

from base import Card

def test_card_initialization():
    card = Card('S', 'A')
    assert card.suit == 'S'
    assert card.rank == 'A'

def test_card_equality():
    card1 = Card('H', 'K')
    card2 = Card('H', 'K')
    card3 = Card('D', 'K')
    
    assert card1 == card2
    assert card1 != card3
    # Verificación de comportamiento cuando el tipo no es Card
    assert (card1 == "HK") is False
    assert (card1 == None) is False

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
    card = Card('BJ', 'A')
    assert card.get_index() == 'BJA'

def test_card_valid_attributes():
    # Validar que los atributos de clase existen y contienen los valores esperados
    assert 'S' in Card.valid_suit
    assert 'A' in Card.valid_rank

def test_card_all_combinations():
    # Iterar sobre las constantes de clase definidas en el código fuente
    for suit in Card.valid_suit:
        for rank in Card.valid_rank:
            card = Card(suit, rank)
            assert card.suit == suit
            assert card.rank == rank
            assert str(card) == rank + suit
            assert card.get_index() == suit + rank

def test_card_hash_uniqueness():
    # Verificar la unicidad del hash basada en la fórmula interna
    hashes = set()
    for suit in Card.valid_suit:
        for rank in Card.valid_rank:
            card = Card(suit, rank)
            h = hash(card)
            assert h not in hashes
            hashes.add(h)