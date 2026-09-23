import pytest
import sys
import types
from unittest.mock import MagicMock

# Dado que el entorno de ejecución carece de dependencias externas como 'numpy'
# que son importadas en la jerarquía del proyecto, debemos inyectar los módulos 
# faltantes en sys.modules para permitir que el código fuente sea importado 
# exitosamente por Python.

sys.modules['numpy'] = MagicMock()
sys.modules['gin_rummy'] = MagicMock()
sys.modules['gin_rummy.game'] = MagicMock()

# Ajustar el path para permitir la importación del archivo action_event.py
sys.path.append('/Users/javierapalacio/Documents/GitHub/testing-t1/Public_Proyects/gin_rummy')

# Importamos del archivo objetivo
from action_event import (
    ActionEvent, ScoreNorthPlayerAction, ScoreSouthPlayerAction,
    DrawCardAction, PickUpDiscardAction, DeclareDeadHandAction,
    GinAction, DiscardAction, KnockAction,
    score_player_0_action_id, score_player_1_action_id,
    draw_card_action_id, pick_up_discard_action_id,
    declare_dead_hand_action_id, gin_action_id,
    discard_action_id, knock_action_id
)
import utils

def test_action_event_equality():
    a1 = ActionEvent(1)
    a2 = ActionEvent(1)
    a3 = ActionEvent(2)
    assert a1 == a2
    assert a1 != a3
    assert a1 != "not an ActionEvent"

def test_get_num_actions():
    assert ActionEvent.get_num_actions() == knock_action_id + 52

def test_decode_action_basic():
    assert isinstance(ActionEvent.decode_action(score_player_0_action_id), ScoreNorthPlayerAction)
    assert isinstance(ActionEvent.decode_action(score_player_1_action_id), ScoreSouthPlayerAction)
    assert isinstance(ActionEvent.decode_action(draw_card_action_id), DrawCardAction)
    assert isinstance(ActionEvent.decode_action(pick_up_discard_action_id), PickUpDiscardAction)
    assert isinstance(ActionEvent.decode_action(declare_dead_hand_action_id), DeclareDeadHandAction)
    assert isinstance(ActionEvent.decode_action(gin_action_id), GinAction)

def test_decode_action_invalid():
    with pytest.raises(Exception, match="decode_action: unknown action_id=999"):
        ActionEvent.decode_action(999)

def test_action_str_representations():
    assert str(ScoreNorthPlayerAction()) == "score N"
    assert str(ScoreSouthPlayerAction()) == "score S"
    assert str(DrawCardAction()) == "draw_card"
    assert str(PickUpDiscardAction()) == "pick_up_discard"
    assert str(DeclareDeadHandAction()) == "declare_dead_hand"
    assert str(GinAction()) == "gin"

def test_action_event_inheritance_and_ids():
    actions = [
        (ScoreNorthPlayerAction(), score_player_0_action_id),
        (ScoreSouthPlayerAction(), score_player_1_action_id),
        (DrawCardAction(), draw_card_action_id),
        (PickUpDiscardAction(), pick_up_discard_action_id),
        (DeclareDeadHandAction(), declare_dead_hand_action_id),
        (GinAction(), gin_action_id)
    ]
    for action, expected_id in actions:
        assert action.action_id == expected_id