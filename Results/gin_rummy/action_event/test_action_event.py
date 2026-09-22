import pytest
from gin_rummy.action_event import (
    ActionEvent, ScoreNorthPlayerAction, ScoreSouthPlayerAction,
    DrawCardAction, PickUpDiscardAction, DeclareDeadHandAction,
    GinAction, DiscardAction, KnockAction
)
from gin_rummy import Card
import utils

def test_action_event_equality():
    action1 = ActionEvent(1)
    action2 = ActionEvent(1)
    action3 = ActionEvent(2)
    assert action1 == action2
    assert action1 != action3
    assert action1 != "not an action"

def test_get_num_actions():
    assert ActionEvent.get_num_actions() == 110

@pytest.mark.parametrize("action_id, expected_type", [
    (0, ScoreNorthPlayerAction),
    (1, ScoreSouthPlayerAction),
    (2, DrawCardAction),
    (3, PickUpDiscardAction),
    (4, DeclareDeadHandAction),
    (5, GinAction),
])
def test_decode_action_simple(action_id, expected_type):
    action = ActionEvent.decode_action(action_id)
    assert isinstance(action, expected_type)
    assert action.action_id == action_id

def test_decode_action_discard():
    # discard range 6 to 57
    action_id = 6
    action = ActionEvent.decode_action(action_id)
    assert isinstance(action, DiscardAction)
    assert action.action_id == action_id
    assert isinstance(action.card, Card)

def test_decode_action_knock():
    # knock range 58 to 109
    action_id = 58
    action = ActionEvent.decode_action(action_id)
    assert isinstance(action, KnockAction)
    assert action.action_id == action_id
    assert isinstance(action.card, Card)

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

def test_card_actions_str():
    # Mocking behavior via real utils.get_card
    card = utils.get_card(0)
    discard = DiscardAction(card=card)
    knock = KnockAction(card=card)
    
    assert str(discard) == f"discard {str(card)}"
    assert str(knock) == f"knock {str(card)}"

def test_discard_action_logic():
    card = utils.get_card(10)
    action = DiscardAction(card=card)
    # discard_action_id (6) + card_id (10) = 16
    assert action.action_id == 16
    assert action.card == card

def test_knock_action_logic():
    card = utils.get_card(5)
    action = KnockAction(card=card)
    # knock_action_id (58) + card_id (5) = 63
    assert action.action_id == 63
    assert action.card == card