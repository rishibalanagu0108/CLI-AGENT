from config import SYSTEM_PROMPT


class ConversationState:
    def __init__(self):
        # System prompt lives in the messages array (OpenAI format)
        self.messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.iterations = 0
        self.token_usage = {"input": 0, "output": 0}

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, message):
        msg = {"role": "assistant", "content": message.content}
        if message.tool_calls:
            msg["tool_calls"] = [tc.model_dump() for tc in message.tool_calls]
        self.messages.append(msg)

    def add_tool_results(self, results: list[dict]):
        # Each result: {role: "tool", tool_call_id: str, content: str}
        for result in results:
            self.messages.append(result)

    def track_tokens(self, usage):
        self.token_usage["input"]  += usage.prompt_tokens
        self.token_usage["output"] += usage.completion_tokens

    @property
    def total_tokens(self) -> int:
        return self.token_usage["input"] + self.token_usage["output"]
