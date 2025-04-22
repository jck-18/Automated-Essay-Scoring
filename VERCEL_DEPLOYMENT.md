# Vercel Deployment Guide

This guide will walk you through deploying this application to Vercel with the correct environment variable configuration.

## Prerequisites

1. A [Vercel](https://vercel.com) account
2. A [Hugging Face](https://huggingface.co) account and API token
3. Git installed on your local machine

## Step-by-Step Deployment

### 1. Prepare your repository

Make sure your repository is ready for deployment:
- Ensure your code is working locally
- Make sure `.env` is in your `.gitignore` file
- Push your changes to GitHub

### 2. Initial deployment

You can deploy to Vercel in two ways:

#### Option A: Using the Vercel dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Keep the default settings and click "Deploy"

#### Option B: Using the Vercel CLI

1. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Login to Vercel:
   ```
   vercel login
   ```

3. Deploy from your project directory:
   ```
   vercel
   ```

### 3. Configure environment variables

**This step is critical for the application to work correctly!**

1. Go to your project in the Vercel dashboard
2. Navigate to "Settings" → "Environment Variables"
3. Add the following variable:
   - **Name**: `HF_API_TOKEN`
   - **Value**: Your Hugging Face API token
   - **Environments**: Production, Preview, Development

   ![Environment Variables](https://vercel.com/docs/storage/images/env-vars-dashboard.png)

4. Click "Save"

### 4. Redeploy your application

After adding the environment variable, you need to redeploy:

1. Go to the "Deployments" tab
2. Click on the three dots (⋮) next to your latest deployment
3. Select "Redeploy"

Alternatively, you can push a new commit to your repository to trigger a new deployment.

### 5. Test your deployment

After redeployment is complete:

1. Open your Vercel deployment URL
2. Enter a test essay in the text area
3. Click "Analyze Essay"
4. Verify that you receive a meaningful score and feedback

## Troubleshooting Vercel Deployments

### Getting default scores (score of 3 with 50% confidence)

This means the application cannot access the Hugging Face API. Check:

1. Verify your API token is correctly set in Vercel environment variables
2. Check deployment logs for any errors related to API calls
3. Ensure your Hugging Face account and token are active

### API Calls are slow or timing out

Vercel has a 10-second timeout for serverless functions. If your API calls are exceeding this:

1. Consider upgrading to Vercel Pro for extended function execution time
2. Optimize your application to handle timeout cases gracefully

### Error: "Not Found" when accessing your API endpoint

This may happen if your API route is not correctly configured:

1. Check your `vercel.json` configuration
2. Ensure your API route is correctly defined
3. Verify that the API endpoint is at `/api` as expected

## Security Notes

- Never commit your API tokens to your repository
- Regularly rotate your API tokens for better security
- Use environment variables for all sensitive configuration 