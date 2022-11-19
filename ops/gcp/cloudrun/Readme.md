Cloudrun is if you want the easiest, lowest overhead way of running a bot. If you want more flexibility and customizability, check out the `terraform` config.

Since a job times out after a maximum of 1 hour, we get around that by scheduling this job to run every hour, at minute 0

Because these commands are fairly symmetric with Cloud Build, you should be able to plug them into your CI/CD process with little/no lift

Firstly, copy the `.dockerignore` and `Dockerfile` to the root of the bot. Then submit the build to cloudrun

```bash
export REGION="us-central1"
export PROJECT=$(gcloud config get-value project)
export PROJECT_NUMBER=`gcloud projects list | grep $PROJECT | awk '{print $(NF)}'`
export IMAGE="us-docker.pkg.dev/$PROJECT/gcr.io/skip-mev/juno-arb:latest"
export JOB_NAME="skip-mev-juno-arb"
source .env

# Build the image
gcloud builds submit --tag $IMAGE

# Create the job
gcloud beta run jobs create $JOB_NAME \
    --image $IMAGE \
    --region $REGION \
    --task-timeout 1h \
    --set-env-vars MNEMONIC="$MNEMONIC"

# Either run the job now
gcloud beta run jobs execute $JOB_NAME --region $REGION

# Or schedule the job
gcloud scheduler jobs create http $JOB_NAME \
    --location $REGION \
    --schedule "0 * * * *" \
    --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT/jobs/$JOB_NAME:run" \
    --http-method POST \
    --oauth-service-account-email $PROJECT_NUMBER-compute@developer.gserviceaccount.com

# To delete the job and cancel any scheduled executions
gcloud beta run jobs delete $JOB_NAME
```

You can monitor job executions at https://console.cloud.google.com/run and view logs at https://console.cloud.google.com/run/jobs/details/$REGION/$JOB_NAME/executions