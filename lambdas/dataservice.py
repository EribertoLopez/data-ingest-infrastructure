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

def processHTS(event, context):
    dynamodb = boto3.client('dynamodb')
    metadata = findMetadata()
    df, fileFormat = readFile(event['filename'])
    if fileFormat == 'Long':
        df = processLongFormat(df)
        print(addMetadata(df, metadata).columns)
    if fileFormat == 'Matrix':
        df = processMatrixFormat(df)
        print(addMetadata(df, metadata).columns)

    for row in df.values[:10] :
        well, value, channel, id_, platebarcode, runid, warpid = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
        add_to_db = dynamodb.put_item(
                TableName='htsprocessed', 
                Item={
                    'well' : {'S' : str(well)},
                    'value' : {'N' : str(value)},
                    'channel' : {'S' : str(channel)},
                    'id' : {'N' : str(id_)},
                    'platebarcode' : {'S' : str(platebarcode)},
                    'runId' : {'S' : str(runid)},
                    'warpId' : {'S' : str(warpid)}
                    })

    return {
        "statusCode": 200,
        "body": json.dumps({
            'hello_from': 'something.',
            'dataType': 'HTS_DATA',
            'route': '/HTS-Data',
            'event': event
        })
    }

def readFile(filename):
    """
    
    """
    SkiprowsLongFormat = 16 
    filepath = 's3://{}/{}'.format('strateos-ds-hts-dummy', filename)
    fs = s3fs.S3FileSystem()

    try : 
        return pd.read_csv(filepath, header=None), 'Matrix'
    except :
        return pd.read_csv(filepath, header=None, skiprows=SkiprowsLongFormat, encoding="ISO-8859-1"), 'Long'
    
def parseFirstColumn(series):
    """
    
    """
    parser = lambda x : [x.split(':')[0], int(x.split(':')[1])]
    return series.apply(parser).apply(pd.Series)

def flatteningChannels(df):
    """
    
    """
    flattenedChannels = pd.DataFrame()
    for channel in ['ChannelA', 'ChannelB', 'ChannelRatio']:
        temp = df[['Well', channel]].rename(columns={channel:'Value'})
        temp['Channel'] = channel.split('l')[-1]
        flattenedChannels = pd.concat([flattenedChannels, temp])
    return flattenedChannels

def processLongFormat(df):
    """
    
    """
    df.rename(columns={0:'ToParse', 1:'ChannelB', 2:'ChannelRatio'}, inplace=True)
    parsed = parseFirstColumn(df['ToParse']).rename(columns={0:'Well', 1:'ChannelA'})
    df.drop('ToParse', 
            axis=1, 
            inplace=True)
    df = pd.concat([parsed, df], axis=1)
    df = flatteningChannels(df)

    return df

def getWellLetterConfig(df):
    """
    
    """
    numberOfLetters = int(df.shape[0] / 3)
    formatedAlphabet = ascii_letters.split('z')[1] + ascii_letters.split('z')[0]
    return formatedAlphabet[:numberOfLetters]

def getChannelList(indexSeries):
    """
    
    """
    numberOfChannels = 3
    switchChannelIndex = indexSeries.shape[0] / numberOfChannels
    channels = []
    for index in indexSeries: 
        if index < switchChannelIndex :
            channels.append('A')
        elif index < switchChannelIndex * 2 :
            channels.append('B')
        else : 
            channels.append('Ratio')
    return channels

def processMatrixFormat(df):
    """
    
    """
    wellLetterConfig = getWellLetterConfig(df)
    df['Channel'] = getChannelList(df.index)
    newStruc = []
    for channel in df.Channel.unique():
        for row, letter in zip(df[df['Channel'] == channel].drop('Channel', axis=1).values, wellLetterConfig) : 
            for index, well_value in enumerate(row) : 
                if index + 1 < 10:
                    newStruc.append([letter + "0" + str(index + 1), well_value, channel])
                else : 
                    newStruc.append([letter + str(index + 1), well_value, channel ])

    return pd.DataFrame(newStruc, columns=['Well', 'Value', 'Channel'])

def findMetadata():
    """
    
    """
    metadata = {'id': 1,
            'plateBarcode': 'AM00000656',
            'runId': 'r1f57rf77jbdsd', 
            'warpId': 'warpid'}
    return metadata

def addMetadata(df, metadata):
    """
    
    """
    df['id'] = metadata['id']
    df['plateBarcode'] = metadata['plateBarcode']
    df['runId'] = metadata['runId']
    df['warpId'] = metadata['warpId']
    return df 
