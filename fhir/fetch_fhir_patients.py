import argparse
import requests
import json
import os
import boto3
import pandas as pd
from datetime import datetime

# Constants
FHIR_API_URL = "https://hapi.fhir.org/baseR4/Patient?_count=1000"  # can be modified

# AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Utility: Parse FHIR Patient data
def extract_patient_data(entry):
    resource = entry.get("resource", {})
    patient_id = resource.get("id")
    name = resource.get("name", [{}])[0]
    gender = resource.get("gender")
    birth_date = resource.get("birthDate")
    full_name = " ".join(name.get("given", []) + [name.get("family", "")]).strip()
    
    return {
        "patient_id": patient_id,
        "full_name": full_name,
        "gender": gender,
        "birth_date": birth_date
    }

# Option 1: Save to local CSV
def save_to_csv(data, file_path="patients.csv"):
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"✅ Data saved locally to {file_path}")

# Option 2: Upload CSV to S3
def save_to_s3(data, bucket_name, object_key):
    df = pd.DataFrame(data)
    csv_buffer = df.to_csv(index=False)
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_buffer)
    print(f"✅ Data uploaded to S3: s3://{bucket_name}/{object_key}")

# Option 3: Save to DynamoDB
def save_to_dynamodb(data, table_name):
    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for item in data:
            batch.put_item(Item=item)
    print(f"✅ Data written to DynamoDB table: {table_name}")

# Main function
def main(destination, bucket=None, key=None, table=None):
    print(f"📡 Fetching FHIR data from {FHIR_API_URL}")
    response = requests.get(FHIR_API_URL, headers={"Accept": "application/fhir+json"})
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch data. Status code: {response.status_code}")
        return

    fhir_data = response.json()
    entries = fhir_data.get("entry", [])
    extracted = [extract_patient_data(e) for e in entries]

    if destination == "csv":
        save_to_csv(extracted)
    elif destination == "s3":
        if not bucket or not key:
            print("❌ S3 bucket and key must be provided.")
            return
        save_to_s3(extracted, bucket, key)
    elif destination == "dynamodb":
        if not table:
            print("❌ DynamoDB table name must be provided.")
            return
        save_to_dynamodb(extracted, table)
    else:
        print("❌ Invalid destination. Choose from csv, s3, or dynamodb.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest FHIR Patient data")
    parser.add_argument("--destination", required=True, choices=["csv", "s3", "dynamodb"])
    parser.add_argument("--bucket", help="S3 bucket name (if destination is s3)")
    parser.add_argument("--key", help="S3 object key (if destination is s3)")
    parser.add_argument("--table", help="DynamoDB table name (if destination is dynamodb)")
    
    args = parser.parse_args()
    main(args.destination, args.bucket, args.key, args.table)

