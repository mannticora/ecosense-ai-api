import os
import uuid
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException

load_dotenv()

LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")
LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")

TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION")

VISION_KEY = os.getenv("AZURE_VISION_KEY")
VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")

client = TextAnalyticsClient(
    endpoint=LANGUAGE_ENDPOINT,
    credential=AzureKeyCredential(LANGUAGE_KEY)
)

app = FastAPI(title="EcoSense AI API")


# ---------- Funciones reutilizables ----------

def get_sentiment(text: str) -> dict:
    response = client.analyze_sentiment(documents=[text])[0]
    return {
        "sentiment": response.sentiment,
        "confidence_scores": {
            "positive": response.confidence_scores.positive,
            "neutral": response.confidence_scores.neutral,
            "negative": response.confidence_scores.negative,
        }
    }

def analyze_image(image_url: str) -> dict:
    path = "vision/v3.2/analyze"
    constructed_url = VISION_ENDPOINT + path

    params = {"visualFeatures": "Description,Tags"}
    headers = {
        "Ocp-Apim-Subscription-Key": VISION_KEY,
        "Content-Type": "application/json"
    }
    body = {"url": image_url}

    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    result = response.json()

    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail=f"Error de Azure Vision: {result['error']['message']}"
        )

    return {
        "caption": result["description"]["captions"][0]["text"],
        "caption_confidence": result["description"]["captions"][0]["confidence"],
        "tags": [tag["name"] for tag in result["tags"][:10]]
    }

def translate_to_spanish(text: str) -> dict:
    path = "/translate"
    constructed_url = TRANSLATOR_ENDPOINT + path
    params = {"api-version": "3.0", "to": "es"}
    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }
    body = [{"text": text}]

    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    result = response.json()[0]

    return {
        "detected_language": result["detectedLanguage"]["language"],
        "translated_text": result["translations"][0]["text"]
    }


# ---------- Modelos de entrada ----------

class TextInput(BaseModel):
    text: str


# ---------- Endpoints ----------

@app.get("/")
def root():
    return {"message": "EcoSense AI API funcionando 🌱"}


@app.post("/analyze/sentiment")
def analyze_sentiment(input: TextInput):
    return {"text": input.text, **get_sentiment(input.text)}


@app.post("/translate")
def translate_text(input: TextInput):
    return {"original_text": input.text, **translate_to_spanish(input.text)}


@app.post("/report/analyze")
def analyze_report(input: TextInput):
    return {
        "original_text": input.text,
        **translate_to_spanish(input.text),
        **get_sentiment(input.text)
    }

class ImageInput(BaseModel):
    image_url: str


@app.post("/analyze/image")
def analyze_image_endpoint(input: ImageInput):
    return analyze_image(input.image_url)
