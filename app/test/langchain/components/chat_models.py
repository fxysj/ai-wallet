# pip install -qU "langchain[openai]"
from openai import api_key, base_url

from app.config import settings
from langchain.chat_models import init_chat_model
model = init_chat_model("gpt-4o-mini",model_provider="openai",api_key=settings.OPENAI_API_KEY,base_url=settings.OPENAI_API_BASE_URL)
res = model.invoke("Hello, world!")
print(res)
# https://python.langchain.com/docs/integrations/chat/