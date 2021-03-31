import requests
import json
import os
import base64
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def consumer(event, context):
    streamName = os.environ['STREAMNAME']
    logger.info('Streaming from: ' + streamName)
    logger.info(f"Number of records: {len(event['Records'])}")
    body = {
        "hello_from": "app.consumer",
        "recordsConsumed": []
    }
    apiEndpoint = f"https://{os.environ['APIID']}.execute-api.{os.environ['APIREG']}.amazonaws.com/{os.environ['APISTAGE']}"
    for r in event['Records']:
        logger.info("Processesing record: ", r)
        message = base64.b64decode(r['kinesis']['data']).decode('utf-8')
        message = json.dumps(message)
        
        servicePath = '/process'
        serviceRoute = apiEndpoint + servicePath
        logger.info("POST to: ", serviceRoute)
        
        logger.info("data from record: ", message)
        requests.post(serviceRoute, json=message)
        
        body['recordsConsumed'].append({
            'record': r,
            'serviceRoute': serviceRoute,
        })
        
        logger.info('POST to http://cheminformatics.transcripticapps.com:5050/device/dataset/process/AcousticLiquidHandler')
        resp = requests.post(
            'http://cheminformatics.transcripticapps.com:5050/device/dataset/process/AcousticLiquidHandler',
            json=message
        )
        
    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

