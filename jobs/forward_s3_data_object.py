import requests

API_ID = 'vad0ls6yx4'
REGION = 'us-west-2'
STAGE = 'strateos-data-ingest-dev-ingest-stage'
ENDPOINT = 'data-upload-type'
GET_DATA_TYPE_URL = f'https://{API_ID}.execute-api.{REGION}.amazonaws.com/{STAGE}/{ENDPOINT}'

def handler(event, context):
    print('Invoking forwarding service...')

    data = event
    resp = requests.post(
        GET_DATA_TYPE_URL,
        data = data
    )

    print(resp)
