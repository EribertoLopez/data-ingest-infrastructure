import requests
import json

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

def mycoolfunction(event, context):
    print('S3 client')
    print('find object')
    print('forward object to PostGres')