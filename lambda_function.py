import jwt
import sys
import logging
import os
import json
import psycopg2
from boto3 import client as boto3_client
from dotenv import load_dotenv
from datetime import timedelta, datetime

load_dotenv()
SECRET = os.getenv("SECRET")

def lambda_handler(event, context):
    print("*********** the event is: *************")
    print(event)

    cpf = event["cpf"]
    user = event["user"]
    email = event["email"]

    return autenticate(cpf, user, email)


def autenticate(cpf, user, email):
    print(f"SECRET={SECRET}")

    lambda_client = boto3_client('lambda')
    users_payload = {"cpf": cpf}
    response = lambda_client.invoke(FunctionName="tech-challenge-users-lambda",
        InvocationType='RequestResponse',
        Payload=json.dumps(users_payload)
    )
            
    response_status_code = response["StatusCode"]
    if response_status_code == 200:
        response_str = response["Payload"].read()
        user_json = json.loads(response_str)
        print(f"users_response = {user_json}")
        
        exp = datetime.now() + timedelta(minutes=60)
        print("exp:", exp)
        
        encoded_jwt = jwt.encode({
            "sub": cpf, 
            "user": user, 
            "email": email, 
            "exp": exp,
            "iat": datetime.now(),
            "iss": "Restaurant API Authorizer"
        }, SECRET, algorithm="HS256")
    
        return {
            "accessToken": encoded_jwt,
            "type": "Bearer",
            "exp": exp.strftime("%d/%m/%Y %H:%M:%S")
        }
    else:
        if response_status_code == 404:
            return {
                'statusCode': 404,
                'body': 'User not found'
            }
        else:
            return {
                'statusCode': 403,
                'body': 'HTTP Error 403 – Forbidden'
            }
    

if __name__ == '__main__':
    print("--- Running locally ---")
    context = None
    event = {'cpf': '11122233344', 'user': 'fabiano', 'email': 'fabianogoes@gmail.com'}
    print(lambda_handler(event, context))