# Essay Score Evaluator

A cloud-ready application that scores essays and provides AI-powered feedback using open-source LLMs.

## Features

- Essay scoring using lightweight open-source models
- AI-powered feedback on grammar, structure, and content
- Single-page web application with clean UI
- Serverless deployment for Vercel and Netlify
- Memory-efficient design for cost-effective cloud hosting

## Deployment Options

### Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   cd api
   python index.py
   ```

### Vercel Deployment

1. Install Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Login to Vercel:
   ```
   vercel login
   ```

3. Deploy to Vercel:
   ```
   vercel
   ```

4. For production deployment:
   ```
   vercel --prod
   ```

### Netlify Deployment

1. Install Netlify CLI:
   ```
   npm install -g netlify-cli
   ```

2. Login to Netlify:
   ```
   netlify login
   ```

3. Deploy to Netlify:
   ```
   netlify deploy
   ```

4. For production deployment:
   ```
   netlify deploy --prod
   ```

### Configuration

Environment variables can be set in the Vercel or Netlify dashboard:

- `USE_LIGHTWEIGHT_MODELS`: Set to "true" (recommended for serverless)
- `MODEL_URL`: URL to custom model file (optional)

## API Usage

The API endpoint is available at `/api/predict`:

```json
POST /api/predict
{
  "text": "Your essay text here...",
  "feedback_required": true
}
```

Response:
```json
{
  "score": 5,
  "confidence": 0.92,
  "feedback": [
    "Grammar feedback...",
    "Clarity feedback...",
    "Structure feedback..."
  ]
}
```

## Architecture

For serverless deployment on Vercel/Netlify, this application:

1. Uses lightweight models (DistilBERT and Flan-T5-small) for memory efficiency
2. Implements efficient model caching
3. Delivers an in-browser UI without requiring a separate frontend
4. Leverages serverless functions to scale automatically

## Models

The application uses:
- DistilBERT for lightweight essay scoring
- Google's Flan-T5-small for generating feedback

Both models run completely on serverless infrastructure without external API dependencies 