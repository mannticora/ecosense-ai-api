from fastapi import Depends
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
import uuid
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException
from typing import Optional
from openai import AzureOpenAI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()

LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")
LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")

TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION")

VISION_KEY = os.getenv("AZURE_VISION_KEY")
VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")

OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

API_KEY = os.getenv("ECOSENSE_API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")
CDMX_API_URL = os.getenv("CDMX_API_URL")


def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key inválida o faltante"
        )
    return key

openai_client = AzureOpenAI(
    api_key=OPENAI_KEY,
    azure_endpoint=OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION
)

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

def get_environmental_analysis(pollutant: str, value: float, unit: str) -> str:
    system_prompt = (
        "Eres un asistente experto en calidad del aire para la Ciudad de México. "
        "Explicas datos de contaminantes de forma clara para ciudadanos sin "
        "conocimiento técnico, y das recomendaciones prácticas de salud. "
        "Sé conciso: máximo 3 oraciones."
    )

    user_prompt = (
        f"El nivel de {pollutant} es {value} {unit}. "
        f"¿Qué significa esto y qué recomendación le darías a alguien en CDMX?"
    )

    response = openai_client.chat.completions.create(
        model=OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=600,
        reasoning_effort="low"
    )

    return response.choices[0].message.content

def get_latest_measurement(pollutant: str) -> dict:
    url = f"{CDMX_API_URL}/measurements/"
    params = {"pollutant": pollutant, "limit": 1}

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos disponibles para el contaminante '{pollutant}'"
        )

    return data[0]

# ---------- Modelos de entrada ----------

class TextInput(BaseModel):
    text: str


# ---------- Endpoints ----------

@app.get("/")
def root():
    return {"message": "EcoSense AI API funcionando 🌱"}


@app.post("/analyze/sentiment", dependencies=[Depends(verify_api_key)])
def analyze_sentiment(input: TextInput):
    return {"text": input.text, **get_sentiment(input.text)}


@app.post("/translate", dependencies=[Depends(verify_api_key)])
def translate_text(input: TextInput):
    return {"original_text": input.text, **translate_to_spanish(input.text)}

class ReportInput(BaseModel):
    text: str
    image_url: Optional[str] = None


@app.post("/report/analyze", dependencies=[Depends(verify_api_key)])
def analyze_report(input: ReportInput):
    result = {
        "original_text": input.text,
        **translate_to_spanish(input.text),
        **get_sentiment(input.text)
    }

    if input.image_url:
        result["image_analysis"] = analyze_image(input.image_url)

    return result

class ImageInput(BaseModel):
    image_url: str


@app.post("/analyze/image", dependencies=[Depends(verify_api_key)])
def analyze_image_endpoint(input: ImageInput):
    return analyze_image(input.image_url)

class EnvironmentalInput(BaseModel):
    pollutant: str
    value: float
    unit: str

@app.post("/analyze/environmental", dependencies=[Depends(verify_api_key)])
def analyze_environmental(input: EnvironmentalInput):
    analysis = get_environmental_analysis(input.pollutant, input.value, input.unit)
    return {
        "pollutant": input.pollutant,
        "value": input.value,
        "unit": input.unit,
        "ai_analysis": analysis
    }

@app.get("/analyze/live-air-quality/{pollutant}", dependencies=[Depends(verify_api_key)])
def analyze_live_air_quality(pollutant: str):
    measurement = get_latest_measurement(pollutant)

    analysis = get_environmental_analysis(
        measurement["pollutant"],
        measurement["value"],
        measurement["unit"]
    )

    return {
        "station": measurement["station"],
        "zone": measurement["zone"],
        "pollutant": measurement["pollutant"],
        "value": measurement["value"],
        "unit": measurement["unit"],
        "timestamp": measurement["timestamp"],
        "ai_analysis": analysis
    }

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/dashboard")
def dashboard():
    return FileResponse("frontend/index.html")
