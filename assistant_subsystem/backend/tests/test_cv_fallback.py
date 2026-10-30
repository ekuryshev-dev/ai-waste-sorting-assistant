from cv_fallback_classes import ImageFallbackClassifier
from chat_handler_classes import PromptBuilder
from data_handler_classes import RulesRepo, RecyclingRule, Category
from llm_access_classes import LLMMockClient

GOOD = '{"material": "paper", "category": "recyclable", "instructions": "Blue bin."}'


def make(tst_sess, reply, retries = 2):
    llm = LLMMockClient(reply)
    clf = ImageFallbackClassifier(llm, RulesRepo(tst_sess), PromptBuilder("Classify."), retries)
    return clf, llm


def test_valid_reply_returns_category_and_instructions(tst_sess):
    clf, _ = make(tst_sess, GOOD)
    result = clf.classify(b"img")
    assert result.category == Category.recyclable
    assert result.instructions == "Blue bin."


def test_json_inside_other_text_is_found(tst_sess):
    clf, _ = make(tst_sess, "Sure! ```json\n" + GOOD + "\n```")
    assert clf.classify(b"img").material == "paper"


def test_invalid_reply_is_retried_then_unknown(tst_sess):
    clf, llm = make(tst_sess, "blah", retries = 2)
    assert clf.classify(b"img").category == Category.unknown
    assert llm.calls == 3


def test_rules_and_image_reach_the_model(tst_sess):
    tst_sess.add(RecyclingRule(region="DE", material="paper", category=Category.recyclable))
    tst_sess.commit()
    clf, llm = make(tst_sess, GOOD)
    clf.classify(b"img", "image/png", "DE")
    assert "paper: recyclable" in llm.received[0]["content"]
    assert llm.received[1]["content"][0]["image_url"]["url"].startswith("data:image/png;base64,")