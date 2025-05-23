from fastapi import FastAPI, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional
import json
from http.server import BaseHTTPRequestHandler
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Hugging Face API configuration
HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "")  # Set this in your Vercel environment variables
# Updated to more appropriate models for essay scoring
SCORE_MODEL_API = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
FEEDBACK_MODEL_API = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# Request/Response models
class EssayRequest(BaseModel):
    text: str
    feedback_required: Optional[bool] = True

class EssayResponse(BaseModel):
    score: int
    confidence: float
    feedback: Optional[List[str]] = None

# Prediction and feedback functions using Hugging Face API
def predict_score(text):
    """Predict the score using Hugging Face Inference API"""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # Check if API token is valid
    if not HF_API_TOKEN or HF_API_TOKEN == "your_hugging_face_api_token_here":
        print("WARNING: No valid Hugging Face API token found. Using mock scores.")
        # Return informative mock data
        return 3, 0.5, [0.1, 0.1, 0.2, 0.5, 0.1, 0.0]
    
    # Wait for model to load if needed with a simple retry mechanism
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                SCORE_MODEL_API, 
                headers=headers, 
                json={"inputs": text[:1000], "parameters": {"candidate_labels": ["poor essay", "average essay", "good essay", "excellent essay"]}}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if we got a valid result
                if isinstance(result, dict) and "scores" in result:
                    # Map classification to score ranges (0-5)
                    scores = result["scores"]
                    labels = result["labels"]
                    
                    # Find the most confident classification
                    best_idx = scores.index(max(scores))
                    best_label = labels[best_idx]
                    confidence = scores[best_idx]
                    
                    # Map labels to scores
                    score_map = {
                        "poor essay": 1,
                        "average essay": 3,
                        "good essay": 4,
                        "excellent essay": 5
                    }
                    
                    score = score_map.get(best_label, 3)
                    
                    # Create probabilities for visualization
                    probs = [0.0] * 6  # Assuming scores 0-5
                    probs[score] = confidence
                    
                    return score, confidence, probs
                elif "error" in result and "currently loading" in result["error"]:
                    # Model is still loading, wait and retry
                    time.sleep(2)
                    continue
            
            # For any other issues, return a default score with warning
            print(f"Warning: API returned unexpected response. Status: {response.status_code}")
            return 3, 0.5, [0.1, 0.1, 0.2, 0.5, 0.1, 0.0]
        
        except Exception as e:
            print(f"Error in score prediction: {str(e)}")
            # Try again after a delay
            time.sleep(1)
    
    # If all retries failed, return default values with detailed message
    print("Failed to get scores after multiple retries")
    return 3, 0.5, [0.1, 0.1, 0.2, 0.5, 0.1, 0.0]

def generate_feedback(text):
    """Generate feedback using Hugging Face Inference API"""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # Check if API token is valid
    if not HF_API_TOKEN or HF_API_TOKEN == "your_hugging_face_api_token_here":
        print("WARNING: No valid Hugging Face API token found. Using mock feedback.")
        # Return informative mock data
        return [
            "Unable to analyze grammar. Please set up a valid API token.",
            "Unable to analyze clarity. Please set up a valid API token.",
            "Unable to analyze structure. Please set up a valid API token."
        ]
    
    # Create prompts for different aspects of feedback
    prompts = [
        f"Identify grammar and spelling errors in this essay and provide specific suggestions for improvement: {text[:300]}",
        f"Evaluate the clarity and coherence of this essay. What could be improved?: {text[:300]}",
        f"Analyze the structure and organization of this essay and provide constructive feedback: {text[:300]}"
    ]
    
    feedbacks = []
    for prompt in prompts:
        # Wait for model to load if needed with a simple retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    FEEDBACK_MODEL_API, 
                    headers=headers, 
                    json={"inputs": prompt, "parameters": {"max_length": 150}}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if we got a result
                    if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                        generated_text = result[0]["generated_text"]
                        feedbacks.append(generated_text)
                        break
                    elif "error" in result and "currently loading" in result["error"]:
                        # Model is still loading, wait and retry
                        time.sleep(2)
                        continue
                
                # For any other issues, add a default message
                feedbacks.append("The feedback service is currently experiencing technical difficulties. Please try again later.")
                break
            
            except Exception as e:
                print(f"Error in feedback generation: {str(e)}")
                # Try again after a delay
                time.sleep(1)
        
        # If all retries failed for this prompt
        if len(feedbacks) <= len(prompts) - 1:
            feedbacks.append("Feedback service is currently unavailable. Please ensure your API token is correctly configured.")
    
    return feedbacks

# HTML for the frontend
def get_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Essay Score Evaluator</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            textarea { width: 100%; height: 200px; padding: 10px; margin-bottom: 10px; }
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer; }
            .result { margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .loading { display: none; margin: 20px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; text-align: center; }
            .disclaimer { font-size: 0.8em; color: #666; margin-top: 30px; }
        </style>
    </head>
    <body>
        <h1>📝 Essay Score Evaluator</h1>
        <p>Enter your essay below to get a predicted score and feedback.</p>
        
        <textarea id="essay" placeholder="Type or paste your essay here..."></textarea>
        <button onclick="analyzeEssay()">Analyze Essay</button>
        <div id="loading" class="loading">Analyzing your essay... (This may take a few seconds)</div>
        
        <div id="result" class="result" style="display:none;">
            <h2>Results</h2>
            <div id="score"></div>
            <h3>Feedback</h3>
            <div id="feedback"></div>
        </div>
        
        <div class="disclaimer">
            <p>Note: This application uses AI to evaluate essays. Results should be considered as suggestions rather than definitive assessments.</p>
            <p>Powered by Hugging Face Inference API and Vercel.</p>
        </div>

        <script>
            async function analyzeEssay() {
                const essay = document.getElementById('essay').value;
                if (!essay.trim()) {
                    alert('Please enter an essay to evaluate.');
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    const response = await fetch('/api', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: essay })
                    });
                    
                    const data = await response.json();
                    document.getElementById('score').innerHTML = `<p>🎯 Predicted Score: <strong>${data.score}</strong></p>
                                                                 <p>🔍 Confidence: ${(data.confidence * 100).toFixed(2)}%</p>`;
                    
                    let feedbackHtml = '';
                    data.feedback.forEach((item, index) => {
                        const categories = ['Grammar and Spelling', 'Clarity and Coherence', 'Structure and Organization'];
                        feedbackHtml += `<h4>${categories[index] || 'Feedback'}</h4><p>${item}</p>`;
                    });
                    
                    document.getElementById('feedback').innerHTML = feedbackHtml;
                    document.getElementById('result').style.display = 'block';
                } catch (error) {
                    alert('Error analyzing essay: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    """

# Vercel serverless function handler
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(get_html().encode())
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # Process the essay
        text = data.get('text', '')
        label, confidence, _ = predict_score(text)
        feedbacks = generate_feedback(text)
        
        # Prepare response
        response = {
            'score': label,
            'confidence': float(confidence),
            'feedback': feedbacks
        }
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

# For local testing
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI(title="Essay Scoring API")
    
    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        return HTMLResponse(content=get_html())
    
    @app.post("/api", response_model=EssayResponse)
    async def predict_api(request: EssayRequest):
        # Get score
        label, confidence, _ = predict_score(request.text)
        
        # Get feedback if requested
        feedbacks = generate_feedback(request.text) if request.feedback_required else None
        
        return EssayResponse(
            score=label,
            confidence=float(confidence),
            feedback=feedbacks
        )
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 