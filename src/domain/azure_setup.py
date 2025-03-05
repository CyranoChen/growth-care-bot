import os

from openai import AzureOpenAI

DEFAULT_API_VERSION = "2025-02-01-preview"


def init_openai_service() -> AzureOpenAI:
    """
    https://learn.microsoft.com/en-US/azure/ai-services/openai/reference
    """
    # Get the Azure OpenAI endpoint and token of east-us-2
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_TOKEN"),
        api_version=DEFAULT_API_VERSION,
    )
