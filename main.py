from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
from typing import List
import json
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Get configuration from environment
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
MODEL_PATH = os.getenv("MODEL_PATH", "model10.keras")
METADATA_PATH = os.getenv("METADATA_PATH", "model_metadata.json")

# Global variables for model and data
model = None
symptom_columns = None
disease_labels = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global model, symptom_columns, disease_labels
    
    # Startup
    try:
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        
        # Load the trained model
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"✓ Model loaded successfully from {MODEL_PATH}")
        
        # Check if metadata file exists
        if not os.path.exists(METADATA_PATH):
            raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")
        
        # Load metadata from JSON file
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
        
        symptom_columns = metadata['symptom_columns']
        print(f"✓ Loaded {len(symptom_columns)} symptom columns from metadata")
        
        disease_labels = metadata['disease_labels']
        print(f"✓ Loaded {len(disease_labels)} disease labels from metadata")
        
        print(f"✓ API running in {ENVIRONMENT} mode")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print(f"   Please ensure all required files are present.")
        raise
    except Exception as e:
        print(f"✗ Error loading model or data: {e}")
        raise
    
    yield
    
    # Shutdown
    print("Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Disease Prediction API",
    description="AI-powered disease prediction based on symptoms",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class SymptomsRequest(BaseModel):
    symptoms: List[str]

# Response model
class PredictionResponse(BaseModel):
    predicted_disease: str
    confidence: float
    top_3_predictions: List[dict]

def preprocess_symptoms(symptoms: List[str]) -> np.ndarray:
    """
    Convert list of symptoms to the format expected by the model
    Creates a binary vector where 1 indicates presence of symptom
    """
    # Create a zero vector with length equal to number of symptom columns
    symptom_vector = np.zeros(len(symptom_columns))
    
    # Normalize input symptoms (lowercase and strip whitespace)
    normalized_symptoms = [s.lower().strip() for s in symptoms]
    
    # Set 1 for symptoms that are present
    for idx, symptom_col in enumerate(symptom_columns):
        # Normalize column name for comparison
        normalized_col = symptom_col.lower().strip()
        if normalized_col in normalized_symptoms:
            symptom_vector[idx] = 1
    
    # Reshape to match model input shape (1, num_features)
    return symptom_vector.reshape(1, -1)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Disease Prediction API is running",
        "status": "healthy",
        "model_loaded": model is not None,
        "environment": ENVIRONMENT,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "symptoms_loaded": symptom_columns is not None,
        "diseases_loaded": disease_labels is not None,
        "total_symptoms": len(symptom_columns) if symptom_columns else 0,
        "total_diseases": len(disease_labels) if disease_labels else 0
    }

@app.get("/symptoms")
async def get_symptoms():
    """Get list of all available symptoms"""
    if symptom_columns is None:
        raise HTTPException(status_code=500, detail="Symptom data not loaded")
    
    return {
        "symptoms": symptom_columns,
        "total": len(symptom_columns)
    }

@app.get("/diseases")
async def get_diseases():
    """Get list of all possible diseases"""
    if disease_labels is None:
        raise HTTPException(status_code=500, detail="Disease data not loaded")
    
    return {
        "diseases": disease_labels,
        "total": len(disease_labels)
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_disease(request: SymptomsRequest):
    """
    Predict disease based on provided symptoms
    
    Args:
        request: SymptomsRequest containing list of symptoms
        
    Returns:
        PredictionResponse with predicted disease and confidence scores
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if not request.symptoms or len(request.symptoms) == 0:
        raise HTTPException(status_code=400, detail="No symptoms provided")
    
    try:
        # Preprocess symptoms
        input_vector = preprocess_symptoms(request.symptoms)
        
        # Get model predictions (logits)
        logits = model.predict(input_vector, verbose=0)
        
        # Apply softmax to get probabilities
        probabilities = tf.nn.softmax(logits).numpy()[0]
        
        # Get top 3 predictions
        top_3_indices = np.argsort(probabilities)[-3:][::-1]  # Get indices in descending order
        
        # Prepare top 3 predictions
        top_3_predictions = []
        for idx in top_3_indices:
            top_3_predictions.append({
                "disease": disease_labels[idx],
                "confidence": float(probabilities[idx])
            })
        
        # Get the top prediction
        top_prediction_idx = top_3_indices[0]
        predicted_disease = disease_labels[top_prediction_idx]
        confidence = float(probabilities[top_prediction_idx])
        
        return PredictionResponse(
            predicted_disease=predicted_disease,
            confidence=confidence,
            top_3_predictions=top_3_predictions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/batch")
async def predict_disease_batch(symptoms_list: List[List[str]]):
    """
    Predict diseases for multiple symptom sets
    
    Args:
        symptoms_list: List of symptom lists
        
    Returns:
        List of predictions
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        results = []
        for symptoms in symptoms_list:
            input_vector = preprocess_symptoms(symptoms)
            logits = model.predict(input_vector, verbose=0)
            probabilities = tf.nn.softmax(logits).numpy()[0]
            
            top_3_indices = np.argsort(probabilities)[-3:][::-1]
            
            top_3_predictions = []
            for idx in top_3_indices:
                top_3_predictions.append({
                    "disease": disease_labels[idx],
                    "confidence": float(probabilities[idx])
                })
            
            results.append({
                "symptoms": symptoms,
                "predicted_disease": disease_labels[top_3_indices[0]],
                "confidence": float(probabilities[top_3_indices[0]]),
                "top_3_predictions": top_3_predictions
            })
        
        return {"predictions": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on {HOST}:{PORT}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Allowed origins: {ALLOWED_ORIGINS}")
    uvicorn.run(
        app, 
        host=HOST, 
        port=PORT,
        log_level="info"
    )
