import os

from openai import AzureOpenAI

DEFAULT_API_VERSION = "2024-12-01-preview"


def init_openai_service() -> AzureOpenAI:
    """
    https://learn.microsoft.com/en-US/azure/ai-services/openai/reference
    """
    # Get the Azure OpenAI endpoint and token of sweden-central
    endpoint = str(os.getenv("AZURE_OPENAI_ENDPOINTS").split(",")[1])
    token = str(os.getenv("AZURE_OPENAI_TOKENS").split(",")[1])

    return AzureOpenAI(
        # pylint: disable=consider-using-f-string
        azure_endpoint="https://{}.openai.azure.com/".format(endpoint),
        api_key=token,
        api_version=DEFAULT_API_VERSION,
    )
