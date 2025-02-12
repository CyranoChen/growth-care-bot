import logging

from openai import AzureOpenAI

from src.domain.azure_setup import init_openai_service


class ConversationService:
    def __init__(self):
        self.client: AzureOpenAI = init_openai_service()
        self.model: str = "gpt-4o"
        self.context: list[dict] = self._get_context()

    def _get_context(self) -> str:
        system_prompt = "你是一个语音助手。"
        return [{"role": "system", "content": system_prompt}]

    def chat(self, user_prompt: str) -> str:
        try:
            self.context.append({"role": "user", "content": user_prompt})
            response = self.client.chat.completions.create(
                model=self.model, messages=self.context
            )

            if (
                not response.choices
                or not response.choices[0].message
                or not (result := response.choices[0].message.content)
            ):
                raise Exception("调用llm，无法获取结果")

            self.context.append({"role": "assistant", "content": result})
            return result

        except Exception as exc:
            logging.error("Error in chat_completion: %s", exc)
            return str(exc)
