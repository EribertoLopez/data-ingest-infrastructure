import requests
import json
import boto3

import codecs
import csv
import io
import zipfile


INGEST_S3 = 'dataIngestor-infrastructure-dev-HTSTable-1OH8J5K3CA3D9'
def process(event, context):
    print(f'Get DynamoDB Client...')
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(INGEST_S3)
    
    print('S3 client')
    print('find object')
    bucket_name = 'strateos-ingest-bucket-dev'
    filename = 'test.zip'
    s3, object = get_s3_object(bucket_name, filename)
    print(f'Process .CSV data')
    s3_file = S3File(object)
    with zipfile.ZipFile(s3_file) as zf:
        for datapath in zf.namelist(): # lists all files in zip
            with zf.open(datapath, 'r') as infile:
                reader = csv.reader(io.TextIOWrapper(infile, 'utf-8'))

                headers = next(reader)
                for row in reader:
                    item = {header: val for header, val in zip(headers, row)}
                    # TODO: Is there a better way to batch instead using multiple PUT calls
                    ddbResponse = table.put_item(
                        Item=item
                    )



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

def get_s3_object(bucket_name, filename):
    s3 = boto3.resource('s3')
    object = s3.Object(bucket_name, filename)
    return s3, object
    
class S3File(io.RawIOBase):
    def __init__(self, s3_object):
        self.s3_object = s3_object
        self.position = 0

    def __repr__(self):
        return "<%s s3_object=%r>" % (type(self).__name__, self.s3_object)

    @property
    def size(self):
        return self.s3_object.content_length

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.position = offset
        elif whence == io.SEEK_CUR:
            self.position += offset
        elif whence == io.SEEK_END:
            self.position = self.size + offset
        else:
            raise ValueError("invalid whence (%r, should be %d, %d, %d)" % (
                whence, io.SEEK_SET, io.SEEK_CUR, io.SEEK_END
            ))

        return self.position

    def seekable(self):
        return True

    def read(self, size=-1):
        if size == -1:
            # Read to the end of the file
            range_header = "bytes=%d-" % self.position
            self.seek(offset=0, whence=io.SEEK_END)
        else:
            new_position = self.position + size

            # If we're going to read beyond the end of the object, return
            # the entire object.
            if new_position >= self.size:
                return self.read()

            range_header = "bytes=%d-%d" % (self.position, new_position - 1)
            self.seek(offset=size, whence=io.SEEK_CUR)

        return self.s3_object.get(Range=range_header)["Body"].read()

    def readable(self):
        return True