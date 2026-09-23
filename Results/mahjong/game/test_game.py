import sys
import pytest
from unittest.mock import MagicMock

# Ajustar path para importar game.py
sys.path.append('/home/matilab/Testing_IIC3745/testing-t1/Public_Proyects/mahjong')

# Mock de dependencias externas que causan errores de importación
sys.modules["numpy"] = MagicMock()
sys.modules["numpy.random"] = MagicMock()
sys.modules["mahjong"] = MagicMock()

from game import MahjongGame

def test_init_game():
    game = MahjongGame()
    game.init_game()
    assert hasattr(game, 'dealer')
    assert hasattr(game, 'players')
    assert hasattr(game, 'round')
    assert isinstance(game.players, list)

def test_get_num_actions():
    assert MahjongGame.get_num_actions() == 38

def test_get_num_players():
    game = MahjongGame()
    assert game.get_num_players() == 4

def test_get_player_id():
    game = MahjongGame()
    game.init_game()
    # Accedemos a la propiedad existente a través del objeto round
    assert game.get_player_id() == game.round.current_player

def test_step():
    game = MahjongGame(allow_step_back=True)
    game.init_game()
    # Definimos explícitamente el atributo necesario para deepcopy en step
    game.dealer = MagicMock()
    game.round = MagicMock()
    game.players = []
    game.history = []
    
    # Mockeamos el método interno proceed_round y get_state
    game.round.proceed_round = MagicMock()
    game.round.current_player = 0
    game.get_state = MagicMock(return_value={})
    
    state, player = game.step('play')
    assert state == {}
    assert len(game.history) == 1

def test_step_back():
    game = MahjongGame(allow_step_back=True)
    game.history = [("d1", "p1", "r1")]
    
    result = game.step_back()
    assert result is True
    assert len(game.history) == 0

def test_get_legal_actions():
    state = {'valid_act': ['play'], 'action_cards': ['1m', '2m']}
    assert MahjongGame.get_legal_actions(state) == ['1m', '2m']
    
    state_other = {'valid_act': ['call']}
    assert MahjongGame.get_legal_actions(state_other) == ['call']

def test_is_over():
    game = MahjongGame()
    game.judger = MagicMock()
    # Retorna win, player, _
    game.judger.judge_game.return_value = (True, 3, None)
    
    result = game.is_over()
    assert result is True
    assert game.winner == 3