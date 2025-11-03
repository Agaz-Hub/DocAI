# Disease Prediction API

FastAPI backend server for predicting diseases based on symptoms using a trained Keras model.

## Features

- **POST /predict**: Predict disease from a list of symptoms
- **POST /predict/batch**: Predict diseases for multiple symptom sets
- **GET /symptoms**: Get all available symptoms
- **GET /diseases**: Get all possible diseases
- **GET /**: Health check endpoint

## Installation

### First Time Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Generate metadata file (only needed once if you have the CSV):

```bash
python setup_metadata.py
```

This creates `model_metadata.json` from the CSV file. After this, you can delete the large CSV file!

## Running the Server

```bash
# Using Python directly
python main.py

# Or using Uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Health Check

```
GET /
```

### 2. Get All Symptoms

```
GET /symptoms
```

### 3. Get All Diseases

```
GET /diseases
```

### 4. Predict Disease (Single)

```
POST /predict
Content-Type: application/json

{
  "symptoms": [
    "fever",
    "cough",
    "headache"
  ]
}
```

Response:

```json
{
  "predicted_disease": "influenza",
  "confidence": 0.85,
  "top_3_predictions": [
    {
      "disease": "influenza",
      "confidence": 0.85
    },
    {
      "disease": "common cold",
      "confidence": 0.1
    },
    {
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
```

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
```

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
