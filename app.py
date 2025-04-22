import streamlit as st
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import torch.nn.functional as F
import os
import requests
from pathlib import Path

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

# Title
st.title("📝 Essay Score Evaluator")
st.write("Enter your essay below to get the predicted score based on a fine-tuned BERT model.")

# Essay input
essay = st.text_area("✍️ Your Essay", height=300)

# Load model
try:
    tokenizer, model = load_model()
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.error("Please make sure the model files are correctly placed in the bert_multiclass_model directory.")
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

# Button
if st.button("Predict Score"):
    if essay.strip() == "":
        st.warning("Please enter an essay to evaluate.")
    else:
        with st.spinner("Evaluating..."):
            label, confidence, probs = predict_score(essay)
        st.success(f"🎯 Predicted Score: {label}")
        st.write(f"🔍 Confidence: {confidence * 100:.2f}%")

        # Show probabilities chart
        st.subheader("🔢 Probability Distribution")
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(np.arange(len(probs)), probs, color="skyblue")
        ax.set_xlabel("Score Label")
        ax.set_ylabel("Probability")
        ax.set_title("Model Confidence Distribution")
        st.pyplot(fig)
