import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['VACATION_TABLE_NAME']
table = dynamodb.Table(table_name)  # type: ignore

def lambda_handler(event, context):
    http_method = event['httpMethod']
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    if event['resource'] == '/vacations':
        if http_method == 'GET':
            response = get_vacations(event['queryStringParameters'])
        elif http_method == 'POST':
            response = create_vacation(event['body'])
        else:
            response = {"statusCode": 405, "body": json.dumps("Method Not Allowed")}
    response['headers'] = headers
    return response

def get_vacations(params):
    try:
        cognito_username = params['CognitoUsername']  # Adjust to the correct key name
        response = table.query(
            KeyConditionExpression=Key('CognitoUsername').eq(cognito_username)  # Adjust to the correct attribute name
        )
        return {"statusCode": 200, "body": json.dumps(response['Items'])}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error retrieving vacations: {e}")}

def create_vacation(vacation_data):
    try:
        vacation_data = json.loads(vacation_data)
        table.put_item(Item=vacation_data)
        return {"statusCode": 201, "body": json.dumps("Vacation created successfully!")}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error creating vacation: {e}")}
