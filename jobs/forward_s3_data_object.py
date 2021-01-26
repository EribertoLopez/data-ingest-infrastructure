import requests

API_ID = 'vad0ls6yx4'
REGION = 'us-west-2'
ENDPOINT = 'data-upload-type'
GET_DATA_TYPE_URL = f'https://{API_ID}.execute-api.{REGION}.amazonaws.com/{ENDPOINT}'

def handler(event, context):
    data = event
    resp = requests.post(
        GET_DATA_TYPE_URL,
        data = data
    )

    print(resp)


https://vad0ls6yx4.execute-api.us-west-2.amazonaws.com/data-upload-type