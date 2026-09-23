import pytest
from gin_rummy import Card
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
    a1 = ActionEvent(10)
    a2 = ActionEvent(10)
    a3 = ActionEvent(11)
    assert a1 == a2
    assert a1 != a3
    assert a1 != "not an action"

def test_get_num_actions():
    assert ActionEvent.get_num_actions() == knock_action_id + 52

def test_decode_basic_actions():
    assert isinstance(ActionEvent.decode_action(score_player_0_action_id), ScoreNorthPlayerAction)
    assert isinstance(ActionEvent.decode_action(score_player_1_action_id), ScoreSouthPlayerAction)
    assert isinstance(ActionEvent.decode_action(draw_card_action_id), DrawCardAction)
    assert isinstance(ActionEvent.decode_action(pick_up_discard_action_id), PickUpDiscardAction)
    assert isinstance(ActionEvent.decode_action(declare_dead_hand_action_id), DeclareDeadHandAction)
    assert isinstance(ActionEvent.decode_action(gin_action_id), GinAction)

def test_decode_discard_knock_actions():
    card = utils.get_card(card_id=0)
    
    # Test Discard
    discard = ActionEvent.decode_action(discard_action_id)
    assert isinstance(discard, DiscardAction)
    assert discard.card == card
    
    # Test Knock
    knock = ActionEvent.decode_action(knock_action_id)
    assert isinstance(knock, KnockAction)
    assert knock.card == card

def test_decode_invalid_action_raises():
    with pytest.raises(Exception, match="unknown action_id=999"):
        ActionEvent.decode_action(999)

def test_action_string_representations():
    card = utils.get_card(card_id=0)
    assert str(ScoreNorthPlayerAction()) == "score N"
    assert str(ScoreSouthPlayerAction()) == "score S"
    assert str(DrawCardAction()) == "draw_card"
    assert str(PickUpDiscardAction()) == "pick_up_discard"
    assert str(DeclareDeadHandAction()) == "declare_dead_hand"
    assert str(GinAction()) == "gin"
    assert "discard" in str(DiscardAction(card))
    assert "knock" in str(KnockAction(card))

def test_discard_knock_initialization():
    card = utils.get_card(card_id=5)
    d = DiscardAction(card)
    k = KnockAction(card)
    
    assert d.action_id == discard_action_id + 5
    assert k.action_id == knock_action_id + 5
    assert d.card == card
    assert k.card == card

def test_action_id_ranges():
    # Test boundaries for discard
    assert isinstance(ActionEvent.decode_action(discard_action_id), DiscardAction)
    assert isinstance(ActionEvent.decode_action(discard_action_id + 51), DiscardAction)
    
    # Test boundaries for knock
    assert isinstance(ActionEvent.decode_action(knock_action_id), KnockAction)
    assert isinstance(ActionEvent.decode_action(knock_action_id + 51), KnockAction)