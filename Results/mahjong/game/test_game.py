import pytest
import sys
from copy import deepcopy

# Ajuste de path para el entorno del usuario
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/mahjong')

try:
    from game import MahjongGame
    from mahjong import Dealer, Player, Round, Judger
except ImportError:
    MahjongGame = None

@pytest.mark.skipif(MahjongGame is None, reason="Dependencias no instaladas")
class TestMahjongGame:
    
    def test_init_and_properties(self):
        game = MahjongGame(allow_step_back=True)
        assert game.allow_step_back is True
        assert game.num_players == 4
        game_d = MahjongGame()
        assert game_d.allow_step_back is False

    def test_step_back_logic_robust(self):
        # Detecta mutantes en 'if not self.history' (AddNot, DeleteNot)
        game = MahjongGame(allow_step_back=True)
        game.init_game()
        
        # Debe fallar si no hay historial (if not self.history)
        assert game.step_back() is False
        
        # Debe funcionar si hay historial
        game.step("check")
        assert len(game.history) == 1
        assert game.step_back() is True
        assert len(game.history) == 0

    def test_step_allow_back_logic(self):
        # Detecta mutante 'if not self.allow_step_back'
        # Caso 1: allow_step_back=True (historial DEBE registrarse)
        game = MahjongGame(allow_step_back=True)
        game.init_game()
        game.step("call")
        assert len(game.history) == 1
        
        # Caso 2: allow_step_back=False (historial NO debe registrarse)
        game_no = MahjongGame(allow_step_back=False)
        game_no.init_game()
        game_no.step("fold")
        assert len(game_no.history) == 0

    def test_get_legal_actions_logic(self):
        # Detecta mutantes en la comparación '== ['play']'
        # Probamos con una lista distinta a ['play'] para asegurar rama 'else'
        state_other = {'valid_act': ['call'], 'action_cards': ['1m']}
        res_other = MahjongGame.get_legal_actions(state_other)
        assert res_other == ['call']
        assert state_other['valid_act'] == ['call']

        # Probamos con la lista exacta ['play'] para asegurar rama 'if'
        state_play = {'valid_act': ['play'], 'action_cards': ['1m']}
        res_play = MahjongGame.get_legal_actions(state_play)
        assert res_play == ['1m']
        assert state_play['valid_act'] == ['1m']
        
        # Probamos con una lista que NO es igual a ['play'] pero tiene elementos comparables
        state_diff = {'valid_act': ['other'], 'action_cards': ['2m']}
        res_diff = MahjongGame.get_legal_actions(state_diff)
        assert res_diff == ['other']

    def test_init_game_flow(self):
        game = MahjongGame()
        state, player_id = game.init_game()
        assert isinstance(state, dict)
        assert isinstance(player_id, int)
        assert len(game.players) == 4
        assert hasattr(game, 'dealer')
        assert hasattr(game, 'history')
        assert game.history == []

    def test_get_state_and_player_id(self):
        game = MahjongGame()
        game.init_game()
        pid = game.get_player_id()
        state = game.get_state(pid)
        assert isinstance(state, dict)
        assert game.get_num_players() == 4

    def test_meta_methods(self):
        assert MahjongGame.get_num_actions() == 38

    def test_is_over_logic(self):
        game = MahjongGame()
        game.init_game()
        res = game.is_over()
        assert isinstance(res, bool)
        assert hasattr(game, 'winner')

    def test_step_back_deep_copy(self):
        game = MahjongGame(allow_step_back=True)
        game.init_game()
        game.step("call")
        hist_dealer, hist_players, hist_round = game.history[0]
        assert isinstance(hist_dealer, Dealer)
        assert isinstance(hist_players, list)
        assert isinstance(hist_round, Round)

    def test_step_logic_execution(self):
        game = MahjongGame(allow_step_back=True)
        game.init_game()
        # Verificar estado tras un paso
        state, next_player = game.step("call")
        assert state is not None
        assert isinstance(next_player, int)
        assert game.cur_state == state

    def test_init_game_card_dealing_loop(self):
        game = MahjongGame()
        game.init_game()
        for p in game.players:
            assert hasattr(p, 'hand')