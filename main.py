import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Cargar variables de entorno desde .env
load_dotenv()

KEY = os.getenv("AZURE_LANGUAGE_KEY")
ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")

# Crear cliente de Azure Language
client = TextAnalyticsClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(KEY)
)

app = FastAPI(title="EcoSense AI API")


class TextInput(BaseModel):
    text: str


@app.get("/")
def root():
    return {"message": "EcoSense AI API funcionando 🌱"}


@app.post("/analyze/sentiment")
def analyze_sentiment(input: TextInput):
    response = client.analyze_sentiment(documents=[input.text])[0]

    return {
        "text": input.text,
        "sentiment": response.sentiment,
        "confidence_scores": {
            "positive": response.confidence_scores.positive,
            "neutral": response.confidence_scores.neutral,
            "negative": response.confidence_scores.negative,
        }
    }
