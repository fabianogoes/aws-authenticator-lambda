import jwt
import os
import requests
from datetime import timedelta, datetime

SECRET = os.getenv("SECRET")

def lambda_handler(event, context):
    print("*********** the event is: *************")
    print(event)

    cpf = event["cpf"]
    print(f"cpf = {cpf}")

    return autenticate(cpf)



def autenticate(cpf):
    print(f"SECRET={SECRET}")

    users_payload = {"cpf": cpf}

    base_url = 'http://ad138951fd8104be09fe5a294412a372-107152645.us-east-1.elb.amazonaws.com:8080/customers/cpf/'
    url = base_url + cpf
    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        data = response.json()
        print(data)

        exp = datetime.now() + timedelta(minutes=60)
        print("exp:", exp)
        
        encoded_jwt = jwt.encode({
            "sub": data["cpf"], 
            "user": data["name"], 
            "email": data["email"], 
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
        if response.status_code == 404:
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
    event = {'cpf': '15204180001'}
    print(lambda_handler(event, context))