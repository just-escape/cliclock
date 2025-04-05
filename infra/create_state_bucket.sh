if [ -z "$1" ]; then
  echo "❌ Usage: $0 <BUCKET_NAME>"
  exit 1
fi

BUCKET_NAME=$1

gcloud storage buckets create gs://$BUCKET_NAME --location=europe-west1

cat <<EOF > lifecycle.json
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {
        "numNewerVersions": 10,
        "age": 7
      }
    }
  ]
}
EOF

gcloud storage buckets update gs://$BUCKET_NAME --lifecycle-file=lifecycle.json --versioning
