from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
from typing import List
import json
import os

# Initialize FastAPI app
app = FastAPI(title="Disease Prediction API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and data
model = None
symptom_columns = None
disease_labels = None

# Request model
class SymptomsRequest(BaseModel):
    symptoms: List[str]

# Response model
class PredictionResponse(BaseModel):
    predicted_disease: str
    confidence: float
    top_3_predictions: List[dict]

@app.on_event("startup")
async def load_model_and_data():
    """Load the trained model and metadata on startup"""
    global model, symptom_columns, disease_labels
    
    try:
        # Load the trained model
        model = tf.keras.models.load_model('model10.keras')
        print("✓ Model loaded successfully")
        
        # Load metadata from JSON file
        with open('model_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        symptom_columns = metadata['symptom_columns']
        print(f"✓ Loaded {len(symptom_columns)} symptom columns from metadata")
        
        disease_labels = metadata['disease_labels']
        print(f"✓ Loaded {len(disease_labels)} disease labels from metadata")
        
    except FileNotFoundError as e:
        print(f"✗ Error: metadata file not found. Please run 'setup_metadata.py' first.")
        print(f"   {e}")
        raise
    except Exception as e:
        print(f"✗ Error loading model or data: {e}")
        raise

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
        "model_loaded": model is not None
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
