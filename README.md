# 🌱 EcoSense AI API

API REST que integra 4 servicios de Azure AI para procesar reportes
ciudadanos y datos en tiempo real de calidad del aire en la Ciudad de
México, generando análisis de sentimiento, traducción automática,
análisis de imágenes y recomendaciones de salud mediante IA generativa.

Conectada como microservicio independiente con [CDMX Air Quality API](https://github.com/mannticora/cdmx-air-quality-api),
formando un pipeline completo: datos reales de estaciones de monitoreo →
procesamiento con IA → recomendaciones accionables.

## 🚀 Demo en vivo

- **API:** https://ecosense-api.yellowbay-011c71f1.southcentralus.azurecontainerapps.io/
- **Documentación interactiva (Swagger):** [/docs](https://ecosense-api.yellowbay-011c71f1.southcentralus.azurecontainerapps.io/docs)

## 🧠 Servicios integrados

| Servicio | Endpoint | Función |
|---|---|---|
| Azure AI Language | `POST /analyze/sentiment` | Análisis de sentimiento con score de confianza |
| Azure AI Translator | `POST /translate` | Traducción y detección automática de idioma |
| Azure AI Vision | `POST /analyze/image` | Descripción y etiquetado de imágenes |
| Azure OpenAI (gpt-5-mini) | `POST /analyze/environmental` | Explicaciones y recomendaciones de salud generadas por IA |
| Orquestador multimodal | `POST /report/analyze` | Combina texto, traducción, sentimiento e imagen en un solo análisis |
| Integración CDMX API | `GET /analyze/live-air-quality/{pollutant}` | Consume datos reales de monitoreo y los procesa con IA |

## 🏗️ Arquitectura

CDMX Air Quality API (Railway) ──┐

↓

Cliente → FastAPI (Docker) → Azure Container Apps

↓

Azure AI Language / Translator / Vision / OpenAI

Dos servicios independientes que se comunican vía HTTP — cada uno con
su propio ciclo de despliegue, manejo de errores y timeouts.

## 🎯 Decisiones de arquitectura

- **Microservicios independientes:** EcoSense y CDMX Air Quality API
  se comunican vía HTTP, con aislamiento de fallos (timeouts en
  llamadas externas).
- **Selección de modelo por costo/latencia:** servicios especializados
  (Language, Translator, Vision) para tareas bien definidas; Azure
  OpenAI reservado para razonamiento abierto.
- **Seguridad por diseño:** autenticación por API key, secretos nunca
  en el repositorio, variables de entorno gestionadas por la plataforma
  de despliegue.
- **Pipeline reproducible:** Docker + Azure Container Registry + Azure
  Container Apps, con tests automatizados en cada push vía GitHub Actions.

## 🔐 Autenticación

Todos los endpoints (excepto `/`) requieren el header `X-API-Key`.

## 🛠️ Stack técnico

- **Backend:** Python, FastAPI
- **IA:** Azure AI Language, Translator, Computer Vision, Azure OpenAI
- **Containerización:** Docker
- **Cloud:** Azure Container Apps + Azure Container Registry
- **CI/CD:** GitHub Actions (tests automatizados en cada push)
- **Testing:** pytest con mocks de servicios externos

## ⚙️ Correr localmente

```bash
git clone https://github.com/mannticora/ecosense-ai-api
cd ecosense-ai-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Configura .env con tus credenciales (ver .env.example)
uvicorn main:app --reload
```

## 🧪 Tests

```bash
pytest -v
```

## 🗺️ Roadmap

- Dashboard frontend con visualización geográfica de reportes y métricas en tiempo real
- Migración a Azure AI Foundry Agents para orquestación avanzada
- Despliegue continuo (CD) a Azure Container Apps vía GitHub Actions
- Autenticación basada en roles (JWT)
