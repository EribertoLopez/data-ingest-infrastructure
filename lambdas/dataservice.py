import json
import boto3 
import os 
import s3fs
import pandas as pd 
from string import ascii_letters


def processHTSdata(event, context):
    # Initiation 
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_ressource = boto3.resource('dynamodb')

    # Get DynamoDb table 
    table_name = dynamodb_client.list_tables()['TableNames'][2]
    print('ls table name', table_name)
    print('os table name:', os.getenv('DDB'))
    table = dynamodb_ressource.Table(table_name)

    table_length = len(table.scan()['Items'])
    
    # Get s3 data for long or matrix format and transform it into proper schema for the db 
    bucket_name = 'strateos-ingest-bucket-dev' 
    print(os.getenv('Bucket'))
    metadata = findMetadata()
    df, fileFormat = readFile(event['filename'], bucket_name)
    if fileFormat == 'Long':
        df = processLongFormat(df)
        print(addMetadata(df, metadata).columns)
    if fileFormat == 'Matrix':
        df = processMatrixFormat(df)
        print(addMetadata(df, metadata).columns)
    
    # Populates the db 
    for index, row in enumerate(df.values[:10]) :
        well, value, channel, platebarcode, runid, warpid = row[0], row[1], row[2], row[3], row[4], row[5]
        add_to_db = dynamodb_client.put_item(
                TableName=table_name, 
                Item={
                    'ID' : {'S' : str(index + table_length)},
                    'well' : {'S' : str(well)},
                    'value' : {'S' : str(value)},
                    'channel' : {'S' : str(channel)},
                    'platebarcode' : {'S' : str(platebarcode)},
                    'runId' : {'S' : str(runid)},
                    'warpId' : {'S' : str(warpid)}
                    })

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def readFile(filename, bucket_name):
    """
    
    """
    print('Read')
    SkiprowsLongFormat = 16 
    filepath = 's3://{}/{}'.format(bucket_name, filename)
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
    metadata = {
        'plateBarcode': 'AM00000656',
        'runId': 'r1f57rf77jbdsd', 
        'warpId': 'warpid'
        }
    return metadata

def addMetadata(df, metadata):
    """
    
    """
    df['plateBarcode'] = metadata['plateBarcode']
    df['runId'] = metadata['runId']
    df['warpId'] = metadata['warpId']
    return df 