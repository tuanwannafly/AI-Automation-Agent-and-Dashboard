import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.google_api_key)
model = genai.GenerativeModel("gemini-pro")


async def complete_gemini(messages: list[dict], model_name: str = "gemini-pro") -> str:
    """Non-streaming complete using Gemini."""
    # Convert messages to Gemini format
    prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])
    response = model.generate_content(prompt)
    return response.text


async def stream_gemini(messages: list[dict], model_name: str = "gemini-pro"):
    """Stream tokens using Gemini."""
    prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text