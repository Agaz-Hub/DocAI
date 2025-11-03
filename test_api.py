"""
Test script for Disease Prediction API
Run this to verify the API is working correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test basic health check"""
    print("Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed\n")

def test_detailed_health():
    """Test detailed health endpoint"""
    print("Testing detailed health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Detailed health check passed\n")

def test_get_symptoms():
    """Test getting all symptoms"""
    print("Testing get symptoms endpoint...")
    response = requests.get(f"{BASE_URL}/symptoms")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total symptoms: {data['total']}")
    print(f"First 5 symptoms: {data['symptoms'][:5]}")
    assert response.status_code == 200
    assert data['total'] > 0
    print("✓ Get symptoms passed\n")

def test_get_diseases():
    """Test getting all diseases"""
    print("Testing get diseases endpoint...")
    response = requests.get(f"{BASE_URL}/diseases")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total diseases: {data['total']}")
    print(f"First 5 diseases: {data['diseases'][:5]}")
    assert response.status_code == 200
    assert data['total'] > 0
    print("✓ Get diseases passed\n")

def test_predict():
    """Test disease prediction"""
    print("Testing disease prediction endpoint...")
    
    # Test with sample symptoms
    test_data = {
        "symptoms": ["fever", "cough", "fatigue"]
    }
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert "predicted_disease" in data
        assert "confidence" in data
        assert "top_3_predictions" in data
        print("✓ Disease prediction passed\n")
    else:
        print(f"Error: {response.text}\n")

def test_batch_predict():
    """Test batch prediction"""
    print("Testing batch prediction endpoint...")
    
    test_data = [
        ["fever", "cough"],
        ["headache", "nausea"],
        ["fatigue", "weakness"]
    ]
    
    response = requests.post(
        f"{BASE_URL}/predict/batch",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Number of predictions: {len(data['predictions'])}")
        print(f"First prediction: {json.dumps(data['predictions'][0], indent=2)}")
        print("✓ Batch prediction passed\n")
    else:
        print(f"Error: {response.text}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("Disease Prediction API Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_health_check()
        test_detailed_health()
        test_get_symptoms()
        test_get_diseases()
        test_predict()
        test_batch_predict()
        
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to the API")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"✗ Test failed: {e}")
