class PromptBuilder:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    def rules_transfigure(self, rules):
        lines = []
        for r in rules:
            line = f"- {r.region} | {r.material}: {r.category.name}"
            if r.instructions:
                line += f" ({r.instructions})"
            lines.append(line)
        return "\n".join(lines)

    def build(self, history, rules, question):
        system = f"{self.system_prompt}\n\nRecycling rules:\n{self.rules_transfigure(rules)}"
        past = [{"role": m.role, "content": m.content} for m in history]
        return [{"role": "system", "content": system}] + past + [{"role": "user", "content": question}]


class AssistantService:
    def __init__(self, rules_repo, chat_repo, ai_client, prompt_builder):
        self.rules_repo = rules_repo
        self.chat_repo = chat_repo
        self.ai_client = ai_client
        self.prompt_builder = prompt_builder

    def converse(self, token, question):
        history = self.chat_repo.get_history(token)
        rules = self.rules_repo.get_rules()
        messages = self.prompt_builder.build(history, rules, question)
        reply = self.ai_client.converse(messages)
        self.chat_repo.add_new(token, "user", question)
        self.chat_repo.add_new(token, "assistant", reply)
        return reply

    def get_history(self, token):
        return self.chat_repo.get_history(token)

    def clear_chat(self, token):
        self.chat_repo.clear_chat(token)