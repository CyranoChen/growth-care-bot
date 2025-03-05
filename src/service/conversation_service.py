import logging
from typing import Optional

from openai import AzureOpenAI

from src.domain.azure_setup import init_openai_service


class ConversationService:
    def __init__(self):
        self.client: AzureOpenAI = init_openai_service()
        self.model: str = "gpt-4o-audio-preview"
        self.modalities: list[str] = ["audio", "text"]
        self.audio: dict = {"voice": "nova", "format": "pcm16"}
        self.params: dict = {
            "temperature": 0.1,
            "stream": True,
        }
        self.context: list[dict] = self._get_context()
        self.transcript_: str = ""

    def _get_context(self) -> str:
        system_prompt = "你是一个语音助手，名字叫妞宝。你要尝试用最通俗易懂的方式回答用户的问题，不要超过50字。"
        return [{"role": "system", "content": system_prompt}]

    def _handle_stream_response(self, chunk: dict) -> Optional[str]:
        # print("chunk:", chunk)
        delta = (
            dict(choices[0]).get("delta", {})
            if (choices := chunk.get("choices", None))
            else None
        )

        if chunk.get("object", None) == "chat.completion.chunk" and delta:
            if not (audio := delta.get("audio", None)):
                return None

            if transcript := audio.get("transcript", None):
                self.transcript_ += transcript

            if audio_id := audio.get("id", None):
                self.context.append(
                    {
                        "role": "assistant",
                        "audio": {"id": audio_id},
                    }
                )

            if encoded_audio := audio.get("data", None):
                return encoded_audio

        return None

    def chat(self, encoded_str: str):
        # pylint: disable=too-many-try-statements
        try:
            # set last transcript to empty
            self.transcript_ = ""
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
                **self.params,
            )

            for chunk in response:
                yield self._handle_stream_response(chunk.model_dump())

        # pylint: disable=broad-exception-caught
        except Exception as exc:
            logging.error("Error in chat_completion: %s", exc)
            # pylint: disable=broad-exception-raised
            raise Exception("模型调用失败，请在日志中查看错误信息") from exc
