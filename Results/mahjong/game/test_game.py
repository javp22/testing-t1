import pytest
import sys
import types

# El error ModuleNotFoundError: No module named 'numpy' indica que la dependencia 
# no está disponible en el entorno de ejecución de pytest.
# Para evitar la falla durante la colección de tests causada por el import en game.py,
# inyectamos un módulo ficticio 'numpy' en sys.modules antes de importar 'game'.
# Esto permite que el código fuente cargue sin errores.

mock_numpy = types.ModuleType("numpy")
mock_numpy.random = types.ModuleType("random")
mock_numpy.random.RandomState = lambda: None
sys.modules["numpy"] = mock_numpy

# Mockear dependencias internas que dependen de numpy para evitar errores en init_game
mock_mahjong = types.ModuleType("mahjong")
mock_mahjong.Dealer = type("Dealer", (), {"__init__": lambda self, r: None, "deal_cards": lambda self, p, n: None})
mock_mahjong.Player = type("Player", (), {"__init__": lambda self, i, r: None})
mock_mahjong.Judger = type("Judger", (), {"__init__": lambda self, r: None, "judge_game": lambda self, g: (False, 0, 0)})
mock_mahjong.Round = type("Round", (), {"__init__": lambda self, j, d, n, r: None, "current_player": 0, "proceed_round": lambda self, p, a: None, "get_state": lambda self, p, i: {}, "current_player": 0})
sys.modules["mahjong"] = mock_mahjong

sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/mahjong')

from game import MahjongGame

def test_mahjong_game_initialization():
    game = MahjongGame(allow_step_back=True)
    assert game.allow_step_back is True
    assert game.num_players == 4

def test_get_legal_actions_logic():
    state = {'valid_act': ['play'], 'action_cards': ['1p', '2p']}
    actions = MahjongGame.get_legal_actions(state)
    assert actions == ['1p', '2p']
    assert state['valid_act'] == ['1p', '2p']
    
    state_fixed = {'valid_act': ['pass']}
    actions = MahjongGame.get_legal_actions(state_fixed)
    assert actions == ['pass']

def test_get_num_actions():
    assert MahjongGame.get_num_actions() == 38

def test_game_metadata_methods():
    game = MahjongGame()
    assert game.get_num_players() == 4