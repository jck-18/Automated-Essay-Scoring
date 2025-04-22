# Essay Score Evaluator

A Streamlit web application that uses a fine-tuned BERT model to evaluate and score essays.

## Features

- Upload or type an essay for automatic scoring
- View the confidence level of the predicted score
- Visualize the probability distribution across all possible scores

## Setup Instructions

### Prerequisites

- Python 3.8+
- Required Python packages (install using `pip install -r requirements.txt`)

### Model Setup

The model file is too large for GitHub (417MB+). You have two options:

#### Option 1: Use External Storage (Recommended)

1. Upload the `model.safetensors` file to a cloud storage service (Google Drive, Dropbox, AWS S3, etc.)
2. Generate a direct download link for the file
3. Replace the `MODEL_URL` in `app.py` with your download link:
   ```python
   MODEL_URL = "YOUR_CLOUD_STORAGE_URL_HERE"  # Replace with your actual URL
   ```

#### Option 2: Local Setup

If running locally:
1. Ensure the `bert_multiclass_model` directory contains:
   - `model.safetensors`
   - `config.json`
   - `tokenizer_config.json`
   - `vocab.txt`
   - `special_tokens_map.json`

### Running the App

```bash
streamlit run app.py
```

## Deployment

### Vercel

When deploying to Vercel, ensure:
1. You have updated the `MODEL_URL` to point to your cloud storage
2. Add `requests` to your requirements.txt if not already present

### Other Platforms

For platforms like Heroku, Render, etc., the same process applies - ensure the model is accessible via a URL and that the app can download it at runtime.

## License

[Insert your license information here] 