class LLMError(Exception):
    status_code = 502
    user_message = "The assistant is unavailable right now. Please try again."


class LLMBusyError(LLMError):
    status_code = 503
    user_message = "The assistant is busy right now. Please try again in a moment."


class LLMTimeoutError(LLMError):
    status_code = 504
    user_message = "The assistant took too long to answer. Please try again."