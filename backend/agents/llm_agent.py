import json
import os
from openai import OpenAI
from .base import Agent
from backend.core.schemas import Action

class LLMAgent(Agent):
    def __init__(self, model, base_url=None, mode="tools", provider="openai", **kwargs):
        if mode not in ("plain", "tools"):
            raise ValueError("mode must be plain or tools")
        self.client = OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY") or ("local" if provider != "openai" else None), timeout=45, max_retries=1)
        self.model, self.mode, self.name = model, mode, f"llm:{model}"

    def act(self, observation):
        messages = [{"role": "user", "content": f"Play chess. Choose one legal UCI move. Return only UCI in plain mode, otherwise call make_move. Position: {observation.model_dump_json()}"}]
        if self.mode == "plain":
            r = self.client.chat.completions.create(model=self.model, messages=messages)
            return Action(move=(r.choices[0].message.content or "").strip())
        tools = [
            {"type": "function", "function": {"name": "legal_moves", "description": "List legal UCI moves", "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "make_move", "description": "Choose a legal move", "parameters": {"type": "object", "properties": {"move": {"type": "string", "enum": observation.legal_moves}}, "required": ["move"]}}}]
        for _ in range(4):
            r = self.client.chat.completions.create(model=self.model, messages=messages, tools=tools, tool_choice="required")
            msg = r.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))
            if not msg.tool_calls:
                return Action(move=None)
            for call in msg.tool_calls:
                if call.function.name == "make_move":
                    try:
                        move = json.loads(call.function.arguments).get("move")
                        return Action(move=move if isinstance(move, str) else None)
                    except (ValueError, AttributeError):
                        return Action(move=None)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(observation.legal_moves)})
        return Action(move=None)
