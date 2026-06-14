# 🌱 EcoSense AI API

API REST que demuestra integración práctica de **4 servicios de Azure AI**
para análisis de calidad del aire y reportes ciudadanos en CDMX, alineada
con los conceptos certificados en **Azure AI-900 (AI Fundamentals)**.

## 🚀 Demo en vivo

- **API:** https://ecosense-api.yellowbay-011c71f1.southcentralus.azurecontainerapps.io/
- **Documentación interactiva (Swagger):** [/docs](https://ecosense-api.yellowbay-011c71f1.southcentralus.azurecontainerapps.io/docs)

## 🧠 Servicios de Azure AI integrados

| Servicio | Endpoint | Concepto AI-900 |
|---|---|---|
| Azure AI Language | `POST /analyze/sentiment` | NLP, análisis de sentimiento |
| Azure AI Translator | `POST /translate` | Traducción, detección de idioma |
| Azure AI Vision | `POST /analyze/image` | Visión por computadora, multimodal |
| Azure OpenAI (gpt-5-mini) | `POST /analyze/environmental` | IA generativa, prompt engineering |
| Orquestador multimodal | `POST /report/analyze` | Combina texto + imagen + traducción |

## 🏗️ Arquitectura

Cliente → FastAPI (Docker) → Azure Container Apps

↓

Azure AI Language / Translator / Vision / OpenAI

## 🔐 Autenticación

Todos los endpoints (excepto `/`) requieren header `X-API-Key`.

## 🛠️ Stack técnico

- **Backend:** Python, FastAPI
- **IA:** Azure AI Language, Translator, Computer Vision, Azure OpenAI
- **Containerización:** Docker
- **Cloud:** Azure Container Apps + Azure Container Registry
- **CI/CD:** GitHub Actions (tests automatizados en cada push)
- **Testing:** pytest con mocks de servicios externos

## ⚙️ Correr localmente

\`\`\`bash
git clone https://github.com/mannticora/ecosense-ai-api
cd ecosense-ai-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Configura tu .env con tus propias credenciales de Azure (ver .env.example)
uvicorn main:app --reload
\`\`\`

## 🧪 Tests

\`\`\`bash
pytest -v
\`\`\`

## 🗺️ Roadmap futuro

- Dashboard frontend (React) con visualización geográfica de reportes
- Migración a Azure AI Foundry Agents para orquestación avanzada
- CD automático: despliegue continuo a Azure Container Apps vía GitHub Actions
- Autenticación JWT con roles (ciudadano vs administrador)

## 📜 Sobre este proyecto

Desarrollado como proyecto práctico complementario a la certificación
**Microsoft Azure AI-900 (AI Fundamentals)**, aplicando cada servicio
estudiado en un caso de uso real para la Ciudad de México.
