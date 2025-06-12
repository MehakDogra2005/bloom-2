# Google Cloud Configuration for Bloom-2 Application

# Instructions for setting up Google Cloud Platform integration:

## 1. Enable Required APIs
Run these commands in Google Cloud Shell or with gcloud CLI:

```bash
# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Set your project ID
export PROJECT_ID=YOUR_PROJECT_ID
gcloud config set project $PROJECT_ID
```

## 2. Authentication Setup

### For Local Development:
```bash
# Install gcloud CLI and authenticate
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### For Production (Google Cloud Run):
The application will automatically use the service account attached to Cloud Run.

## 3. Environment Variables

Create a `.env` file with:
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json  # Only for local dev
```

## 4. Generate Doctor Images

### Locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Run the image generator
python generate_doctor_images.py YOUR_PROJECT_ID
```

### On Google Cloud:
```bash
# Deploy to Cloud Run first, then run from Cloud Shell:
gcloud run jobs create doctor-image-generator \
  --image=gcr.io/YOUR_PROJECT_ID/bloom-2 \
  --region=us-central1 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID" \
  --memory=2Gi \
  --cpu=1 \
  --max-retries=1

# Execute the job
gcloud run jobs execute doctor-image-generator --region=us-central1
```

## 5. Deploy to Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bloom-2
gcloud run deploy bloom-2 \
  --image gcr.io/YOUR_PROJECT_ID/bloom-2 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID"
```

## 6. Required Permissions

Your service account needs these IAM roles:
- AI Platform Admin (roles/aiplatform.admin)
- Storage Admin (roles/storage.admin)
- Cloud Run Developer (roles/run.developer)

## 7. Cost Considerations

- Vertex AI Imagen: ~$0.02 per image
- For 22 doctors: ~$0.44 total
- Cloud Storage: Minimal cost for image storage
- Cloud Run: Pay per request

## Troubleshooting

### Common Issues:
1. **Authentication Error**: Ensure gcloud is configured and APIs are enabled
2. **Quota Exceeded**: Check Vertex AI quotas in Google Cloud Console
3. **Image Generation Failed**: Check prompt content and safety filters
4. **File Not Found**: Ensure doctors.json exists in static/data/

### Debug Commands:
```bash
# Check authentication
gcloud auth list

# Check project
gcloud config get-value project

# Check API enablement
gcloud services list --enabled | grep aiplatform

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```
