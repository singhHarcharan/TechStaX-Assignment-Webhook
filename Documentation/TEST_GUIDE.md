# Webhook Testing Guide

This guide explains how to test the GitHub webhook integration for the TechStaX Assignment.

## Prerequisites

1. A GitHub repository with admin access
2. The webhook URL: `https://techstax-assignment-webhook.onrender.com/webhook`
3. Webhook secret (stored securely)

## Setup Instructions

### 1. Configure GitHub Webhook

1. Go to your GitHub repository: [TechStaX-Assignment-ActionRepo](https://github.com/singhHarcharan/TechStaX-Assignment-ActionRepo)
2. Navigate to: `Settings` → `Webhooks` → `Add webhook`
3. Configure the webhook with these settings:
   - **Payload URL**: `https://techstax-assignment-webhook.onrender.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: `your_webhook_secret_here` (use the same secret as in your environment variables)
   - **SSL verification**: Enable "Enable SSL verification"
   - **Events**: Select "Let me select individual events" and choose:
     - `Push`
     - `Pull request`
     - `Merge`
   - **Active**: Checked

### 2. Test Webhook Setup

1. After saving the webhook, GitHub will send a ping event
2. Check the webhook's "Recent Deliveries" section for a green checkmark (✓)

## Testing Different Events

### 1. Push Event Test

1. Make a change to your repository:
   ```bash
   git clone [https://github.com/singhHarcharan/TechStaX-Assignment-ActionRepo.git](https://github.com/singhHarcharan/TechStaX-Assignment-ActionRepo.git)
   cd TechStaX-Assignment-ActionRepo
   touch test.txt
   git add test.txt
   git commit -m "Test push event"
   git push origin main