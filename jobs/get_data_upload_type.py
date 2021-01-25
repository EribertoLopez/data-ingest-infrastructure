def handler(event, context):
    for records in event['Records']:
        bucket = records['s3']['bucket']
        object_key = records['s3']['object']['key']

        print('Bucket: ' + bucket + ' | Object key: ' + object_key)

    return

