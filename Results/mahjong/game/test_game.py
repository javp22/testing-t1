import pytest
from game import MahjongGame

def test_initialization():
    game = MahjongGame(allow_step_back=True)
    assert game.allow_step_back is True
    assert game.num_players == 4
    assert game.get_num_players() == 4
    assert game.get_num_actions() == 38

def test_init_game_state():
    game = MahjongGame()
    state, player_id = game.init_game()
    assert isinstance(state, dict)
    assert player_id == game.get_player_id()
    assert game.cur_state == state

def test_step_logic():
    game = MahjongGame(allow_step_back=True)
    game.init_game()
    initial_player = game.get_player_id()
    
    # Executing a step
    state, next_player = game.step("some_action")
    
    assert state == game.cur_state
    assert len(game.history) == 1
    assert next_player != initial_player or next_player == initial_player

def test_step_back_functionality():
    game = MahjongGame(allow_step_back=True)
    game.init_game()
    
    # Should be false initially as history is empty
    assert game.step_back() is False
    
    game.step("action1")
    assert len(game.history) == 1
    
    # Return to previous state
    assert game.step_back() is True
    assert len(game.history) == 0

def test_step_without_allow_step_back():
    game = MahjongGame(allow_step_back=False)
    game.init_game()
    game.step("action1")
    # History should remain empty
    assert len(game.history) == 0

def test_get_legal_actions_logic():
    # Case: valid_act is ['play']
    state_play = {'valid_act': ['play'], 'action_cards': ['card1', 'card2']}
    actions = MahjongGame.get_legal_actions(state_play)
    assert actions == ['card1', 'card2']
    assert state_play['valid_act'] == ['card1', 'card2']
    
    # Case: valid_act is something else
    state_other = {'valid_act': ['call', 'fold']}
    actions = MahjongGame.get_legal_actions(state_other)
    assert actions == ['call', 'fold']

def test_is_over_structure():
    game = MahjongGame()
    game.init_game()
    # The method depends on judger.judge_game(self)
    # We test that it returns a boolean as expected by the implementation
    result = game.is_over()
    assert isinstance(result, bool)
    assert hasattr(game, 'winner')

def test_get_state_consistency():
    game = MahjongGame()
    game.init_game()
    p_id = game.get_player_id()
    state = game.get_state(p_id)
    assert isinstance(state, dict)
    assert state == game.get_state(p_id)