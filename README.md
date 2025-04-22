# Essay Score Evaluator

A cloud-ready application that scores essays and provides AI-powered feedback using Hugging Face models.

## Features

- Essay scoring using natural language processing
- AI-powered feedback on grammar, structure, and content
- Single-page web application with clean UI
- Serverless deployment for Vercel and Netlify
- API-driven design for reliable performance

## ⚠️ IMPORTANT: API Setup Required

This application requires a Hugging Face API token to function correctly. Without it, you'll receive generic scores and feedback.

### Setting Up Your API Token:

1. Create a free account at [Hugging Face](https://huggingface.co/join)
2. Generate an API token at https://huggingface.co/settings/tokens
3. Add your API token:
   
   **For Vercel deployment:**
   - Go to your project in the Vercel dashboard
   - Go to Settings > Environment Variables
   - Add a variable with key `HF_API_TOKEN` and your token as the value
   - Redeploy your application

   **For local development:**
   - Add your token to the `.env` file (replace the placeholder text with your actual token)

## Deployment Options

### Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your Hugging Face API token in the `.env` file

3. Run the application:
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

5. **IMPORTANT**: Add your Hugging Face API token in the Vercel dashboard under environment variables

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

5. **IMPORTANT**: Add your Hugging Face API token in the Netlify dashboard under environment variables

## Troubleshooting

### My essays always get a score of 3 with 50% confidence

This indicates that the application is not successfully connecting to the Hugging Face API. Check:
1. Have you set up a valid API token in your environment variables?
2. Is your API token correctly formatted?
3. Check the logs for any error messages related to API calls

### The feedback is generic or nonsensical

This typically indicates one of the following issues:
1. Missing or invalid API token
2. API rate limiting (free Hugging Face accounts have limited requests per minute)
3. Models are still loading - try again in a few minutes

### How to test if your API token is working

Run the following curl command (replace YOUR_TOKEN with your actual token):

```
curl -X POST \
  https://api-inference.huggingface.co/models/facebook/bart-large-mnli \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "This is a test"}'
```

If it returns JSON data, your token is working correctly.

## API Usage

The API endpoint is available at `/api`:

```json
POST /api
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

## Models Used

The application uses these Hugging Face models:
- `facebook/bart-large-mnli` for essay classification and scoring
- `facebook/bart-large-cnn` for generating detailed feedback

Both models are accessed via the Hugging Face Inference API. 