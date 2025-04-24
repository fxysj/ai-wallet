from typing import List

from openai import OpenAI
from pydantic import BaseModel
from app.config import settings
class EntitiesModel(BaseModel):
    attributes: List[str]
    colors: List[str]
    animals: List[str]

client = OpenAI(base_url=settings.OPENAI_API_BASE_URL,api_key=settings.OPENAI_API_KEY)
# Sending a completion request to OpenAI
response = client.completions.create(
    model="gpt-4o",
    prompt="The quick brown fox jumps over the lazy dog with piercing blue eyes",
    max_tokens=150,
    stream=True  # Enabling streaming
)
# Processing the streamed response
for event in response:
    if event.get("type") == "response.output_text.delta":
        print(event['delta'], end="")

    elif event.get("type") == "response.error":
        print(f"Error: {event.get('error')}", end="")

    elif event.get("type") == "response.completed":
        print("Completed")

# Final output of the stream
final_response = response.get('choices', [{}])[0].get('text', '')
print(f"Final response: {final_response}")