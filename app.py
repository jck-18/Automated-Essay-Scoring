import streamlit as st
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch
import torch.nn.functional as F
import os
import requests
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

# Constants
MODEL_PATH = "bert_multiclass_model"
MODEL_FILE = "model.safetensors"
# Default to GitHub Release URL - change if using a different storage option
MODEL_URL = "https://github.com/jck-18/Automated-Essay-Scoring/releases/download/v1.0/model.safetensors" 
MAX_LEN = 256
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Download model if not exists
def download_model_if_needed():
    model_file_path = Path(MODEL_PATH) / MODEL_FILE
    
    # Create directory if it doesn't exist
    os.makedirs(MODEL_PATH, exist_ok=True)
    
    # Check if model file exists
    if not model_file_path.exists():
        st.info("Downloading model file (this may take a few minutes)...")
        try:
            # Download the file
            response = requests.get(MODEL_URL, stream=True)
            response.raise_for_status()
            
            # Write to file
            with open(model_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            st.success("Model downloaded successfully!")
        except Exception as e:
            st.error(f"Error downloading model: {str(e)}")
            st.error("Please download the model file manually from GitHub Releases and place it in the bert_multiclass_model directory.")
            st.stop()

# Load model and tokenizer
@st.cache_resource
def load_model():
    # Ensure model is downloaded
    download_model_if_needed()
    
    tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
    model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
    model.to(DEVICE)
    model.eval()
    return tokenizer, model

# Load LLM for feedback (cached for efficiency)
@st.cache_resource
def load_llm():
    # Use a lightweight model from Hugging Face for feedback
    try:
        feedback_generator = pipeline(
            "text2text-generation",
            model="facebook/bart-large-cnn",
            device=0 if torch.cuda.is_available() else -1,
        )
        return feedback_generator
    except Exception as e:
        st.warning(f"Could not load feedback model: {str(e)}. Will continue without feedback feature.")
        return None

# Title
st.title("📝 Essay Score Evaluator")
st.write("Enter your essay below to get the predicted score and feedback based on our models.")

# Essay input
essay = st.text_area("✍️ Your Essay", height=300)

# Tabs for different features
tab1, tab2 = st.tabs(["Score Prediction", "Essay Feedback"])

# Load models
try:
    tokenizer, model = load_model()
    feedback_model = load_llm()
except Exception as e:
    st.error(f"Error loading models: {str(e)}")
    st.error("Please make sure the model files are correctly placed in the appropriate directory.")
    st.stop()

# Predict function
def predict_score(text):
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=MAX_LEN)
    tokens = {k: v.to(DEVICE) for k, v in tokens.items()}
    with torch.no_grad():
        output = model(**tokens)
    logits = output.logits
    probabilities = F.softmax(logits, dim=1).squeeze()
    predicted_label = torch.argmax(probabilities).item()
    confidence = probabilities[predicted_label].item()
    return predicted_label, confidence, probabilities.cpu().numpy()

# Feedback function using the LLM
def generate_feedback(text):
    if feedback_model is None:
        return "Feedback model not available. Please try again later."
    
    # Create prompts for different aspects of feedback
    prompts = [
        f"Identify grammar and spelling errors in this essay: {text[:500]}...",
        f"Suggest improvements for clarity and coherence of this essay: {text[:500]}...",
        f"Evaluate the structure and organization of this essay: {text[:500]}..."
    ]
    
    feedbacks = []
    for prompt in prompts:
        try:
            result = feedback_model(prompt, max_length=150, min_length=30, do_sample=False)
            feedbacks.append(result[0]['generated_text'])
        except Exception as e:
            feedbacks.append(f"Could not generate this feedback: {str(e)}")
    
    return feedbacks

# Button to analyze
if st.button("Analyze Essay"):
    if essay.strip() == "":
        st.warning("Please enter an essay to evaluate.")
    else:
        with st.spinner("Analyzing your essay..."):
            # Get score prediction
            label, confidence, probs = predict_score(essay)
            
            # Get feedback
            feedbacks = generate_feedback(essay)
        
        # Display in tabs
        with tab1:
            st.success(f"🎯 Predicted Score: {label}")
            st.write(f"🔍 Confidence: {confidence * 100:.2f}%")

            # Show probabilities chart
            st.subheader("🔢 Probability Distribution")
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(np.arange(len(probs)), probs, color="skyblue")
            ax.set_xlabel("Score Label")
            ax.set_ylabel("Probability")
            ax.set_title("Model Confidence Distribution")
            st.pyplot(fig)
        
        with tab2:
            st.subheader("📝 Essay Feedback")
            
            # Grammar and spelling
            with st.expander("Grammar and Spelling", expanded=True):
                st.write(feedbacks[0])
            
            # Clarity and coherence
            with st.expander("Clarity and Coherence", expanded=True):
                st.write(feedbacks[1])
            
            # Structure and organization
            with st.expander("Structure and Organization", expanded=True):
                st.write(feedbacks[2])
            
            st.info("Note: This feedback is generated by an AI model and should be used as a general guide only.")

# Add info about the FastAPI deployment
st.sidebar.title("About")
st.sidebar.info(
    "This application is also available as an API endpoint. "
    "Check out the `/docs` endpoint when deployed for API documentation."
)

# FastAPI integration for cloud deployment
if __name__ == "__main__" and os.environ.get("ENABLE_API", "False").lower() == "true":
    import uvicorn
    from fastapi import FastAPI, Body
    from pydantic import BaseModel
    
    class EssayRequest(BaseModel):
        text: str
    
    class EssayResponse(BaseModel):
        score: int
        confidence: float
        feedback: list
    
    app = FastAPI(title="Essay Scoring API")
    
    @app.post("/predict", response_model=EssayResponse)
    async def predict_api(request: EssayRequest):
        # Get score
        label, confidence, _ = predict_score(request.text)
        
        # Get feedback
        feedbacks = generate_feedback(request.text)
        
        return EssayResponse(
            score=label,
            confidence=float(confidence),
            feedback=feedbacks
        )
    
    # Documentation endpoint
    @app.get("/")
    def read_root():
        return {"message": "Welcome to the Essay Scoring API. Go to /docs for documentation."}
    
    # Start the server
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
