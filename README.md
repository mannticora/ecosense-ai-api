# 🌱 EcoSense AI API

API REST que integra 4 servicios de Azure AI para procesar reportes
ciudadanos y datos en tiempo real de calidad del aire en la Ciudad de
México, generando análisis de sentimiento, traducción automática,
análisis de imágenes y recomendaciones de salud mediante IA generativa.

Conectada como microservicio independiente con [CDMX Air Quality API](https://github.com/mannticora/cdmx-air-quality-api),
formando un pipeline completo: datos reales de estaciones de monitoreo →
procesamiento con IA → recomendaciones accionables para ciudadanos.

## 🚀 Demo en vivo

| Recurso | URL |
|---|---|
| Dashboard interactivo | [/dashboard](https://ecosense-api.yellowbay-011c71f1.southcentralus.azurecontainerapps.io/dashboard) |
| Documentación API (Swagger) | [/docs](https://ecosense-api.yellowbay-011c71f1.southcentralus.azurecontainerapps.io/docs) |
| API base | https://ecosense-api.yellowbay-011c71f1.southcentralus.azurecontainerapps.io |

## 🧠 Servicios Azure AI integrados

| Servicio | Endpoint | Función |
|---|---|---|
| Azure AI Language | `POST /analyze/sentiment` | Análisis de sentimiento con score de confianza |
| Azure AI Translator | `POST /translate` | Traducción y detección automática de idioma |
| Azure Computer Vision | `POST /analyze/image` | Descripción y etiquetado de imágenes |
| Azure OpenAI (gpt-5-mini) | `POST /analyze/environmental` | Explicaciones y recomendaciones de salud |
| Orquestador multimodal | `POST /report/analyze` | Combina texto, traducción, sentimiento e imagen |
| Integración CDMX API | `GET /analyze/live-air-quality/{pollutant}` | Datos reales de monitoreo + análisis IA |
| Dashboard | `GET /dashboard` | Frontend interactivo dark mode |

## 🏗️ Arquitectura

CDMX Air Quality API (Railway) ──┐

↓

Cliente → FastAPI (Docker) → Azure Container Apps

↓

Azure AI Language / Translator / Vision / OpenAI (gpt-5-mini)

↓

Dashboard interactivo (/dashboard)

Dos servicios independientes comunicándose vía HTTP — cada uno con
su propio ciclo de despliegue, manejo de errores y timeouts.

## 🎯 Decisiones de arquitectura

- **Microservicios independientes:** EcoSense y CDMX Air Quality API
  se comunican vía HTTP, con aislamiento de fallos (timeouts en
  llamadas externas para evitar cascada de fallos).
- **Selección de modelo por costo/latencia:** servicios especializados
  (Language, Translator, Vision) para tareas bien definidas; Azure
  OpenAI reservado para razonamiento abierto donde se justifica el costo.
- **Seguridad por diseño:** autenticación por API key, secretos nunca
  en el repositorio, variables de entorno gestionadas por Azure Container Apps.
- **Pipeline reproducible:** Docker + Azure Container Registry + Azure
  Container Apps, con versionado explícito de imágenes (no `:latest` en producción).
- **Tests con mocks:** pytest simula servicios externos para mantener
  el CI/CD rápido, gratuito y determinístico.

## 🔐 Autenticación

Todos los endpoints (excepto `/` y `/dashboard`) requieren el header:

X-API-Key: <tu_api_key>

## 🛠️ Stack técnico

- **Backend:** Python 3.12, FastAPI
- **IA:** Azure AI Language, Translator, Computer Vision, Azure OpenAI
- **Containerización:** Docker + Azure Container Registry
- **Cloud:** Azure Container Apps (South Central US)
- **CI/CD:** GitHub Actions — tests automáticos en cada push
- **Testing:** pytest con mocks de servicios externos

## ⚙️ Correr localmente

```bash
git clone https://github.com/mannticora/ecosense-ai-api
cd ecosense-ai-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Completa con tus credenciales de Azure
uvicorn main:app --reload
```

Abre `http://127.0.0.1:8000/dashboard` para el dashboard local.

## 🧪 Tests

```bash
pytest -v
```

## 🗺️ Roadmap

- Despliegue continuo (CD) automático a Azure Container Apps vía GitHub Actions
- Autenticación basada en roles con JWT
- Migración a Azure AI Foundry Agents para orquestación avanzada
- Visualización geográfica de reportes por zona de CDMX
- Alertas automáticas cuando los niveles de contaminantes superan límites OMS
