# Disease Prediction API Server

A FastAPI-powered REST API server that predicts diseases based on symptoms using a trained deep learning model (Keras/TensorFlow).

## 🚀 Quick Start

### Option 1: Use Startup Script

**Windows:**

```bash
start.bat
```

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Setup

```bash
# 1. Activate virtual environment
# Windows:
myenv\Scripts\activate
# Linux/Mac:
source myenv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
python main.py
```

🌐 **Server runs at:** http://localhost:8000

## � API Documentation

Interactive API documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Health & Info

- `GET /` - Basic health check
- `GET /health` - Detailed server status
- `GET /symptoms` - List all available symptoms (377 symptoms)
- `GET /diseases` - List all possible diseases (773 diseases)

### Prediction

- `POST /predict` - Predict disease from symptoms
- `POST /predict/batch` - Batch prediction for multiple cases

### Example Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fever", "cough", "headache"]}'
```

### Example Response

```json
{
  "predicted_disease": "Common Cold",
  "confidence": 0.85,
  "top_3_predictions": [
    { "disease": "Common Cold", "confidence": 0.85 },
    { "disease": "Influenza", "confidence": 0.1 },
    { "disease": "Bronchitis", "confidence": 0.03 }
  ]
}
```

## ⚙️ Configuration

The server can be configured via environment variables in the `.env` file:

| Variable          | Description                            | Default               |
| ----------------- | -------------------------------------- | --------------------- |
| `HOST`            | Server host address                    | `0.0.0.0`             |
| `PORT`            | Server port                            | `8000`                |
| `ENVIRONMENT`     | Mode (`development`/`production`)      | `development`         |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `*`                   |
| `MODEL_PATH`      | Path to Keras model file               | `model10.keras`       |
| `METADATA_PATH`   | Path to metadata JSON                  | `model_metadata.json` |

## 🛠️ Tech Stack

- **FastAPI** - Modern web framework
- **TensorFlow/Keras** - Deep learning model
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python-dotenv** - Environment management

## 📦 Project Structure

```
DocAI/
├── main.py                 # FastAPI server application
├── model10.keras          # Trained ML model
├── model_metadata.json    # Symptoms and disease labels
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── start.bat             # Windows startup script
└── start.sh              # Linux/Mac startup script
```

## 🧪 Testing

Test the API using the included test script:

```bash
python test_api.py
```

Or manually test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Get symptoms
curl http://localhost:8000/symptoms

# Predict disease
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fever", "cough"]}'
```

## 🐳 Docker Support

Run with Docker:

```bash
# Using Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t disease-api .
docker run -p 8000:8000 disease-api
```

## 🚀 Deployment

The server is deployment-ready for:

- **Heroku**: Uses `Procfile` and `runtime.txt`
- **Docker**: Uses `Dockerfile` and `docker-compose.yml`
- **Cloud platforms**: Railway, Render, AWS, GCP, Azure

For production deployment:

1. Set `ENVIRONMENT=production` in `.env`
2. Update `ALLOWED_ORIGINS` with your frontend URLs
3. Use `start-production.sh/.bat` for Gunicorn server

## 🔒 Security Notes

- In production, update `ALLOWED_ORIGINS` to specific domains
- Keep `.env` file secure and never commit it
- Model files are required for server to start

## 📝 Model Information

- **Total Symptoms**: 377
- **Total Diseases**: 773
- **Model Type**: Deep Neural Network (Keras)
- **Input**: Binary vector of symptoms
- **Output**: Disease prediction with confidence scores

## 🐛 Troubleshooting

**Port already in use:**

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Model not loading:**

- Verify `model10.keras` exists in root directory
- Verify `model_metadata.json` exists in root directory

**CORS errors:**

- Update `ALLOWED_ORIGINS` in `.env` file

## 📄 License

Educational/Research Project
"disease": "pneumonia",
"confidence": 0.05
}
]
}

```

### 5. Predict Disease (Batch)

```

POST /predict/batch
Content-Type: application/json

[
["fever", "cough"],
["headache", "nausea"]
]

````

## Example Client Code

### Python Client

```python
import requests

url = "http://localhost:8000/predict"
data = {
    "symptoms": [
        "fever",
        "cough",
        "headache",
        "fatigue"
    ]
}

response = requests.post(url, json=data)
result = response.json()

print(f"Predicted Disease: {result['predicted_disease']}")
print(f"Confidence: {result['confidence']:.2%}")
print("\nTop 3 Predictions:")
for pred in result['top_3_predictions']:
    print(f"  - {pred['disease']}: {pred['confidence']:.2%}")
````

### JavaScript/Fetch Client

```javascript
const url = "http://localhost:8000/predict";
const data = {
  symptoms: ["fever", "cough", "headache", "fatigue"],
};

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(data),
})
  .then((response) => response.json())
  .then((result) => {
    console.log("Predicted Disease:", result.predicted_disease);
    console.log("Confidence:", result.confidence);
    console.log("Top 3 Predictions:", result.top_3_predictions);
  })
  .catch((error) => console.error("Error:", error));
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"symptoms\": [\"fever\", \"cough\", \"headache\"]}"
```

## Notes

- The API expects symptom names to match those in the training dataset
- Symptom matching is case-insensitive
- The model returns top 3 most likely diseases with confidence scores
- CORS is enabled for all origins (update in production for security)
- **Server now uses `model_metadata.json` instead of the large CSV file** (50% smaller deployment!)

## Files Required

- `model10.keras`: Trained Keras model (~50 MB)
- `model_metadata.json`: Symptom and disease metadata (24 KB) - **replaces the 50+ MB CSV!**
