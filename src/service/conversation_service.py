import logging

from openai import AzureOpenAI
from openai.types.chat import ChatCompletionAudio

from src.domain.azure_setup import init_openai_service


class ConversationService:
    def __init__(self):
        self.client: AzureOpenAI = init_openai_service()
        self.model: str = "gpt-4o-audio-preview"
        self.modalities: list[str] = ["audio", "text"]
        self.audio: dict = {"voice": "nova", "format": "wav"}
        self.context: list[dict] = self._get_context()

    def _get_context(self) -> str:
        system_prompt = "你是一个语音助手，名字叫妞宝。你要尝试用最通俗易懂的方式回答用户的问题。不要超过50字。"
        return [{"role": "system", "content": system_prompt}]

    def chat(self, encoded_str: str) -> ChatCompletionAudio:
        """response example:
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": null,
                "refusal": null,
                "audio": {
                    "id": "audio_abc123",
                    "expires_at": 1729018505,
                    "data": "<bytes omitted>",
                    "transcript": "Yes, golden retrievers are known to be ..."
                }
            },
            "finish_reason": "stop"
        }
        """
        # pylint: disable=too-many-try-statements
        try:
            self.context.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {"data": encoded_str, "format": "wav"},
                        }
                    ],
                }
            )
            response = self.client.chat.completions.create(
                model=self.model,
                modalities=self.modalities,
                audio=self.audio,
                messages=self.context,
            )

            if (
                not response.choices
                or not response.choices[0].message
                or not (response.choices[0].message.audio)
            ):
                logging.error("response: %s", response.model_dump_json())
                # pylint: disable=broad-exception-raised
                raise Exception("模型调用失败，无法获取结果")

            result = response.choices[0].message.audio
            self.context.append(
                {
                    "role": "assistant",
                    "audio": {"id": result.id},
                }
            )
            return result

        # pylint: disable=broad-exception-caught
        except Exception as exc:
            logging.error("Error in chat_completion: %s", exc)
            # pylint: disable=broad-exception-raised
            raise Exception("模型调用失败，请在日志中查看错误信息") from exc
