import requests
import json
import os

def consumer(event, context):
    apiEndpoint = f"https://{os.environ['APIID']}.execute-api.{os.environ['APIREG']}.amazonaws.com/{os.environ['APISTAGE']}"
    streamName = os.environ['STREAMNAME']
    print('Streaming from: ' + streamName)
    print(f"Number of records: {len(event['Records'])}")
    for r in event['Records']:
        print(r)
        # look a the data field and map the data type
        if 'csv' in r['kinesis']['data'].lower():
            print('hts post to processing endpoint')
            requests.post(apiEndpoint + '/process')
        # if data type then post to endpoint
    
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "hello_from": "app.consumer",
                "dataType": event['Records'][0]['kinesis']['data'],
                "route": "/process",
                "event": event,
            }
        ),
    }

testcontext = None # <__main__.LambdaContext object at 0x7f294975a8b0>
testevent = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "hts-data-key",
                "sequenceNumber": "49615134504910266808533590511982557943402697614740684802",
                "data": "test.csv",
                "approximateArrivalTimestamp": 1612673359.612,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49615134504910266808533590511982557943402697614740684802",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::384739123065:role/sls-dataingestor-poc-dev-us-west-2-lambdaRole",
            "awsRegion": "us-west-2",
            "eventSourceARN": "arn:aws:kinesis:us-west-2:384739123065:stream/DataIngestorStream-dev",
        }
    ]
}

def test_consumer():
    streamName = 'STEAMNAME' # os.environ['STREAMNAME']
    print('Streaming from: ' + streamName)
    print(testevent)
    print(f"Number of records: {len(testevent['Records'])}")
    for r in testevent['Records']:
        print(r)
        # look a the data field and map the data type
        if 'csv' in r['kinesis']['data'].lower() and 'hts' in r['kinesis']['partitionKey'].lower():
            # requests.post('')
            print('hts post to processing endpoint')
        # if data type then post to endpoint
    
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            'hello_from': 'app.stream_consumer',
            'stream': streamName,
            'dataType': 'HTS_DATA',
            'route': '/HTS-Data',
            'event': testevent
        })
    }


if __name__ == '__main__':
    test_consumer()



