import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

vacation_table_name = os.environ['VACATION_TABLE_NAME']
vacation_table = dynamodb.Table(vacation_table_name)

def lambda_handler(event, context):
    http_method = event['httpMethod']
    # /manager Routes
    if event['resource'] == '/manager':
        if http_method == 'GET':
            return get_all_items()
        elif http_method == 'POST':
            body = json.loads(event['body'])
            return create_item(body)
    # /vacations Routes
    elif event['resource'] == '/vacations':
        if http_method == 'GET':
            from_date = event['queryStringParameters'].get('from')
            to_date = event['queryStringParameters'].get('to')
            return get_vacations_between_dates(from_date, to_date)
    # /vacations/approvals Routes
    elif event['resource'] == '/vacations/approvals':
        if http_method == 'GET':
            return get_approved_vacations()

    return {"statusCode": 404, "body": json.dumps("Resource not found")}

# MANAGERS TABLE FUNCTIONS
def get_all_items():
    try:
        response = table.scan()
        items = response.get('Items', [])
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error getting items: {e}")
        }

def create_item(body):
    try:
        table.put_item(Item=body)
        return {
            'statusCode': 201,
            'body': json.dumps('Item created')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error creating item: {e}")
        }

# VACATION TABLE FUNCTIONS
def get_vacations_between_dates(from_date, to_date):
    try:
        response = vacation_table.scan(
            FilterExpression="StartDate BETWEEN :from_date AND :to_date",
            ExpressionAttributeValues={
                ":from_date": from_date,
                ":to_date": to_date
            }
        )
        return {"statusCode": 200, "body": json.dumps(response['Items'])}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error scanning items: {e}")}

def get_approved_vacations():
    try:
        response = vacation_table.scan(
            FilterExpression="isApproved = :is_approved",
            ExpressionAttributeValues={
                ":is_approved": True
            }
        )
        return {"statusCode": 200, "body": json.dumps(response['Items'])}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error scanning items: {e}")}
