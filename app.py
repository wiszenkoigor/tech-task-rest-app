import json
import sys
import psycopg2
import boto3
import os
from botocore.exceptions import ClientError
from flask import Flask, jsonify



app = Flask(__name__)

secrets_client = boto3.client('secretsmanager', region_name='eu-central-1')

def get_secret():

    secret_name = "rds!db-f0136c82-a824-425a-b174-e439f0dff702"
    region_name = "eu-central-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        return get_secret_value_response['SecretString']
    except ClientError as e:
        raise e

    

@app.route('/')
def hello():
    try:
        db_secret = get_secret()
        db_creds = json.loads(db_secret)
        print("fetched secret")
        conn = psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=db_creds['username'],
            password=db_creds['password'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        )
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()[0]
        conn.close()
        return jsonify({'message': f'Connected to RDS ({db_version})'})
    except Exception as e:
        import traceback
        return traceback.format_exc()
        return jsonify({'error': str(e)})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
