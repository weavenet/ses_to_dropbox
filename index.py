#!/usr/bin/env python

from record import Record 

def process_record(record):
    key = record['s3']['object']['key']
    bucket = record['s3']['bucket']['name']
    region = record['awsRegion']

    record = Record(key, bucket, region)
    record.process()

def process_event(event):
    for record in event['Records']:
	print "Processing record '%s'." % record
	process_record(record)

def handler(event, context):
    print "Processing event '%s'." % event
    process_event(event)
    print "Processing event '%s' complete." % event
