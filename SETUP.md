# Local Setup Instructions

## Setting Up Your API Token

To use this application, you'll need to set up your Hugging Face API token:

### For Local Development

1. Create a free account at [Hugging Face](https://huggingface.co/join)
2. Generate an API token at https://huggingface.co/settings/tokens
3. Open the `.env` file in the root directory
4. Replace `your_hugging_face_api_token_here` with your actual token
5. Save the file

Example:
```
HF_API_TOKEN=hf_your_actual_token_here
```

### For Vercel Deployment

When deploying to Vercel, you should **not** commit your API token. Instead:

1. Go to your Vercel project dashboard
2. Navigate to Settings > Environment Variables
3. Add a new environment variable:
   - **Name**: `HF_API_TOKEN`
   - **Value**: Your Hugging Face API token
4. Click "Save"
5. Redeploy your application for the changes to take effect

![Vercel Environment Variables](https://vercel.com/docs/storage/images/env-vars-dashboard.png)

### For Netlify Deployment

Similar to Vercel, for Netlify:

1. Go to your Netlify project dashboard
2. Navigate to Site settings > Build & deploy > Environment
3. Add a new environment variable:
   - **Key**: `HF_API_TOKEN`
   - **Value**: Your Hugging Face API token
4. Click "Save"
5. Redeploy your application

## Important Security Note

The `.env` file is in `.gitignore` to prevent accidentally committing sensitive information. 
Never commit your API tokens or other secrets to a git repository!

## Running the Application

After setting up your API token:

1. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   cd api
   python index.py
   ```

3. Open your browser to http://localhost:8000 