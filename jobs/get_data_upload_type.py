def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        print('Bucket: ' + bucket + ' | Object key: ' + object_key)

    return

