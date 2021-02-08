#!/bin/bash

# echo -n "Enter your Kinesis Stream Name: "
# read name
# echo -n "Enter the path to your data file:"
# read path
# echo -n "Enter a partition key for this record:"
# read partitionkey
aws kinesis put-record --stream-name "DataIngestorStream-2-dev" --data "./test.csv" --partition-key "my-partitionkey"