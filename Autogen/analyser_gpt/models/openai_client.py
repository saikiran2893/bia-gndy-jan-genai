from config.constant import Config
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

def get_model_client():

    # Create an agent that uses the OpenAI GPT-4o model.
    model_client = OpenAIChatCompletionClient(
        model=Config.MODEL_NAME,
        # api_key="YOUR_API_KEY",
    )
    return model_client
    