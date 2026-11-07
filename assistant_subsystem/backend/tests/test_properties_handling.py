import pytest
from chat_handler_classes import PromptBuilder
from cv_fallback_classes import ImageFallbackClassifier
from data_handler_classes import RulesRepo
from llm_access_classes import LLMMockClient


def test_negative_retries_are_rejected(tst_sess):
    with pytest.raises(ValueError):
        ImageFallbackClassifier(LLMMockClient(), RulesRepo(tst_sess), PromptBuilder("Mock prompt"), max_retries = -1)