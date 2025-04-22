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

The model file is too large for GitHub (417MB+). You have three options:

#### Option 1: Download from GitHub Release (Recommended)

1. Go to the [Releases](https://github.com/jck-18/Automated-Essay-Scoring/releases) section of this repository
2. Download the `model.safetensors` file from the latest release
3. Place it in the `bert_multiclass_model` directory

#### Option 2: Use External Storage

1. Upload the `model.safetensors` file to a cloud storage service (Google Drive, Dropbox, AWS S3, etc.)
2. Generate a direct download link for the file
3. Replace the `MODEL_URL` in `app.py` with your download link:
   ```python
   MODEL_URL = "YOUR_CLOUD_STORAGE_URL_HERE"  # Replace with your actual URL
   ```

#### Option 3: Local Setup (if you already have the model)

If running locally and you already have the model file:
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
1. You have updated the `MODEL_URL` to point to either the GitHub Release download URL or another cloud storage location
2. Add `requests` to your requirements.txt if not already present

### Other Platforms

For platforms like Heroku, Render, etc., the same process applies - ensure the model is accessible via a URL and that the app can download it at runtime.

## License

[Insert your license information here] 