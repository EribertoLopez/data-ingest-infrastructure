import requests
import json
import os

def consumer(event, context):
    streamName = os.environ['STREAMNAME']
    print('Streaming from: ' + streamName)
    print(f"Number of records: {len(event['Records'])}")
    body = {
        "hello_from": "app.consumer",
        "recordsConsumed": []
    }
    apiEndpoint = f"https://{os.environ['APIID']}.execute-api.{os.environ['APIREG']}.amazonaws.com/{os.environ['APISTAGE']}"
    for r in event['Records']:
        print("Processesing record: ", r)
        servicePath = '/process'
        serviceRoute = apiEndpoint + servicePath
        print("POST to: ", serviceRoute)
        resp = requests.post(serviceRoute, data=r)
        body['recordsConsumed'].append({
            'record': r,
            'serviceRoute': serviceRoute,
            'response': resp
        })

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
