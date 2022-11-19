If you want to use a persistent GCE instance to manage your bot, use this config. A persistent GCE instance offers more flexibility in line with more overhead, say if you want to run sidecar services and so on. Use the cloudrun config if you're just looking for the quick and dirty.

Firstly, set up your environment and create the VM

```bash
export TF_VAR_zone="us-central1-c"
export TF_VAR_instance_name="skip-mev-juno-arb"
export PROJECT=$(gcloud config get-value project)

# Copy the .template files
cp variables.template variables.tf
cp provider.template provider.tf

# Dynamic substitution for the terraform config
sed -i "" s/PROJECT_ID/$PROJECT/g variables.tf
sed -i "" s/PROJECT_ID/$PROJECT/g provider.tf
sed -i "" s/ZONE/$TF_VAR_zone/g variables.tf
sed -i "" s/ZONE/$TF_VAR_zone/g provider.tf
sed -i "" s/INSTANCE_NAME/$TF_VAR_instance_name/g variables.tf

# You can always reset to the template with the following
# sed -i "" s/$PROJECT/PROJECT_ID/g variables.template
# sed -i "" s/$PROJECT/PROJECT_ID/g provider.template
# sed -i "" s/$TF_VAR_zone/ZONE/g variables.template
# sed -i "" s/$TF_VAR_zone/ZONE/g provider.template
# sed -i "" s/$TF_VAR_instance_name/INSTANCE_NAME/g variables.template

# Initialize terraform state in GCS
terraform init \
      -backend-config="bucket=$PROJECT-tfstate" \
      -backend-config="prefix=$TF_VAR_instance_name"
terraform apply
```

Now, we can copy the bot to the instance. Make sure the mnemonic in your `.env` is popualted correctly.

```bash
gcloud compute scp --recurse ../../../*.py ../../../*.json ../../../*.txt ../../../.env ubuntu@$TF_VAR_instance_name:/home/ubuntu --zone $TF_VAR_zone

# SSH onto the machine and follow setup instructions for the bot, namely
gcloud compute ssh --zone $TF_VAR_zone ubuntu@$TF_VAR_instance_name --tunnel-through-iap --project $PROJECT

# Set up dependencies to run from the root, so that the startup script can function
sudo apt update
sudo apt-get install python3-pip -y
sudo mkdir -p /app && sudo cp ~/.env ~/* /app
cd /app
sudo pip install -r requirements.txt
exit
```

[Optionally, but recommended] install the cloudwatch ops agent
*You can also install via the console, by visiting https://console.cloud.google.com/monitoring/dashboards/resourceList/gce_instance*

```bash
cd ~/ && curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
```

Finally, restart the instance. The bot is initialized via the startup script specified in the terraform config

```bash
gcloud compute instances reset $TF_VAR_instance_name --zone $TF_VAR_zone
```

To verify the startup script worked, you can run `sudo journalctl -u google-startup-scripts.service` and can view logs by querying the following in the logs explorer

```bash
resource.type="gce_instance"
sourceLocation.function="main.setupAndRunScript"
resource.labels.instance_id="THE_INSTANCE_ID_RETURNED_FROM_TERRAFORM"
```