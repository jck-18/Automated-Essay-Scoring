from fastapi import FastAPI, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import sys
import torch
from pathlib import Path
import requests
from dotenv import load_dotenv
from typing import List, Optional
import json
from http.server import BaseHTTPRequestHandler

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Define model paths and constants
MODEL_PATH = os.environ.get("MODEL_PATH", "bert_multiclass_model")
MODEL_FILE = os.environ.get("MODEL_FILE", "model.safetensors")
MODEL_URL = os.environ.get("MODEL_URL", "https://github.com/jck-18/Automated-Essay-Scoring/releases/download/v1.0/model.safetensors")
DEVICE = "cpu"  # Always use CPU for serverless deployments
MAX_LEN = 256

# Setup templates for the web UI
templates = Jinja2Templates(directory="templates")

# Request/Response models
class EssayRequest(BaseModel):
    text: str
    feedback_required: Optional[bool] = True

class EssayResponse(BaseModel):
    score: int
    confidence: float
    feedback: Optional[List[str]] = None


# For Vercel/Netlify, we'll use lighter models and load them on demand
def get_scoring_pipeline():
    """Get a lightweight text classification pipeline"""
    try:
        from transformers import pipeline
        classifier = pipeline(
            "text-classification", 
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1  # Use CPU
        )
        return classifier
    except Exception as e:
        print(f"Error loading scoring model: {str(e)}")
        return None

def get_feedback_pipeline():
    """Get a lightweight text generation pipeline"""
    try:
        from transformers import pipeline
        generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",  # Much smaller than BART
            device=-1  # Use CPU
        )
        return generator
    except Exception as e:
        print(f"Error loading feedback model: {str(e)}")
        return None

# Simple in-memory cache
model_cache = {}

def get_model(model_type):
    """Get model from cache or load it"""
    if model_type in model_cache:
        return model_cache[model_type]
    
    if model_type == "scoring":
        model = get_scoring_pipeline()
    elif model_type == "feedback":
        model = get_feedback_pipeline()
    else:
        return None
        
    model_cache[model_type] = model
    return model

# Prediction and feedback functions
def predict_score(text):
    """Predict the score using a lightweight model appropriate for serverless"""
    classifier = get_model("scoring")
    if not classifier:
        return 0, 0.0, [0.0, 0.0]
        
    # For simplicity, map positive/negative to score ranges
    result = classifier(text[:512])[0]  # Limit text length
    score = 5 if result["label"] == "POSITIVE" else 2
    confidence = result["score"]
    
    # Create mock probabilities for visualization
    probs = [0.0] * 6  # Assuming scores 0-5
    probs[score] = confidence
    
    return score, confidence, probs

def generate_feedback(text):
    """Generate feedback using a lightweight model"""
    generator = get_model("feedback")
    if not generator:
        return ["Feedback model not available."]
    
    # Create prompts for different aspects of feedback
    prompts = [
        f"Identify grammar errors in: {text[:200]}",
        f"How to improve clarity: {text[:200]}",
        f"Evaluate structure of: {text[:200]}"
    ]
    
    feedbacks = []
    for prompt in prompts:
        try:
            result = generator(prompt, max_length=100, do_sample=False)
            feedbacks.append(result[0]['generated_text'])
        except Exception as e:
            feedbacks.append(f"Could not generate feedback: {str(e)}")
    
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
            .loading { display: none; }
        </style>
    </head>
    <body>
        <h1>📝 Essay Score Evaluator</h1>
        <p>Enter your essay below to get a predicted score and feedback.</p>
        
        <textarea id="essay" placeholder="Type or paste your essay here..."></textarea>
        <button onclick="analyzeEssay()">Analyze Essay</button>
        <div id="loading" class="loading">Analyzing your essay...</div>
        
        <div id="result" class="result" style="display:none;">
            <h2>Results</h2>
            <div id="score"></div>
            <h3>Feedback</h3>
            <div id="feedback"></div>
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