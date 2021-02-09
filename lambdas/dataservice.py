import requests
import json
import boto3

def process(event, context):
    print(f'Get DynamoDB Client...')
    print(f'Process .CSV data')
    print(f'PUT with client')
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            'hello_from': 'dataservice.',
            'dataType': 'HTS_DATA',
            'route': '/HTS-Data',
            'event': event
        })
    }

def readingfiles3(event, context):
    s3 = boto3.resource('s3')
    fileList = [i for i in s3.Bucket('strateos-ds-hts-dummy').objects.all()]
    fileobj = 3.Bucket('strateos-ds-hts-dummy').Object(fileList[1])
    print(fileList[1])
