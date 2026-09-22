import sys
import pytest

# Asegurar que el directorio del archivo base esté en el path de importación
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/gin_rummy')

from base import Card

def test_card_initialization():
    card = Card('H', 'A')
    assert card.suit == 'H'
    assert card.rank == 'A'
    assert isinstance(card.suit, str)
    assert isinstance(card.rank, str)

def test_card_equality():
    card1 = Card('S', 'T')
    card2 = Card('S', 'T')
    card3 = Card('S', 'A')
    card4 = Card('H', 'T')
    
    # Pruebas de identidad y valores
    assert card1 == card2
    assert card1 != card3
    assert card1 != card4
    
    # Prueba de mutante en operador de igualdad (AND)
    # Si cambiara a OR, el test fallaría
    assert (Card('S', 'A') == Card('S', 'A')) is True
    assert (Card('S', 'A') == Card('H', 'A')) is False
    assert (Card('S', 'A') == Card('S', '2')) is False

def test_card_inequality_with_other_types():
    card = Card('S', 'A')
    # Verificación de NotImplemented
    assert (card == 123) is False
    assert (card == "SA") is False

def test_card_hash_math():
    # Verificación estricta de la fórmula: rank_index + 100 * suit_index
    # valid_suit = ['S', 'H', 'D', 'C', 'BJ', 'RJ'] (Indices 0 a 5)
    # valid_rank = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K'] (Indices 0 a 12)
    
    c1 = Card('S', 'A') # 0 + 100*0 = 0
    assert hash(c1) == 0
    
    c2 = Card('C', '9') # index C=3, index 9=8 -> 8 + 100*3 = 308
    assert hash(c2) == 308
    
    c3 = Card('RJ', 'K') # index RJ=5, index K=12 -> 12 + 100*5 = 512
    assert hash(c3) == 512
    
    assert hash(c1) != hash(c2)
    assert hash(c2) != hash(c3)

def test_card_str_representation():
    card = Card('D', 'Q')
    assert str(card) == 'QD'
    assert str(Card('BJ', 'A')) == 'ABJ'

def test_card_get_index():
    card = Card('C', '7')
    assert card.get_index() == 'C7'
    assert card.get_index() == card.suit + card.rank

def test_card_constants_integrity():
    assert len(Card.valid_suit) == 6
    assert len(Card.valid_rank) == 13
    assert Card.valid_suit[0] == 'S'
    assert Card.valid_rank[0] == 'A'
    assert Card.valid_rank[-1] == 'K'

def test_all_combinations_and_hash_uniqueness():
    hashes = set()
    for suit in Card.valid_suit:
        for rank in Card.valid_rank:
            card = Card(suit, rank)
            h = hash(card)
            # Asegurar que cada carta tiene un hash único
            assert h not in hashes, f"Colisión de hash detectada en {suit}{rank}"
            hashes.add(h)
            
            # Verificar retorno de métodos
            assert str(card) == rank + suit
            assert card.get_index() == suit + rank

def test_hash_mutation_resistance():
    # Test para asegurar que el hash usa las constantes correctas
    # Si se muta el orden de valid_suit o valid_rank, este test fallará
    c = Card('H', '2')
    # H index 1, 2 index 1 -> 1 + 100*1 = 101
    assert hash(c) == 101