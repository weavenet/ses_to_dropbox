#!/usr/bin/env python

import boto3
import dropbox
import email
import json
import os
import time
import random, string

class Record(object):
    def __init__(self, key, bucket, region):
        self.key = key
        self.bucket = bucket
        self.region = region
        self.expires_in = 604800 # 7days

        self.name = self.__generate_name()
        self.dbx = dropbox.Dropbox(self.__dropbox_access_token())
        self.client = boto3.client('s3', region_name=self.region)

    def __dropbox_access_token(self):
        return os.environ['DROPBOX_ACCESS_TOKEN']

    def __generate_self_signed_url(self, bucket, key):
        url = self.client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=self.expires_in)
        return url.encode('ascii','ignore')

    def __generate_name(self):
        return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time())) + "-" + self.__randomword(4)

    def __randomword(self, length):
       return ''.join(random.choice(string.lowercase) for i in range(length))

    def __upload_data_to_dropbox(self, data, file_name):
        print("Uploading file to dropbox '%s'.") % file_name
        self.dbx.files_upload(data, file_name)
        print("Upload file '%s' to dropbox complete.") % file_name

    def __download_s3_object(self):
        print("Dowloading key '%s' from bucket '%s' in region '%s'.") % (self.key, self.bucket, self.region)
        response = self.client.get_object(Bucket=self.bucket, Key=self.key)
        body = response['Body'].read()
        print("Dowloading key '%s' from bucket '%s' in region '%s' complete.") % (self.key, self.bucket, self.region)
        return body

    def __upload_eml_to_dropbox(self, raw_eml_data):
        file_name = "/" + self.name + ".eml"
        print("Uploading eml file to '%s'.") % (file_name)
        self.__upload_data_to_dropbox(raw_eml_data, file_name)

    def __parse_from_eml(self, eml):
        try:
            msg = email.message_from_string(eml)
            return msg['from']
        except Exception as e:
            print("Error parsing text", e)

        print("Unable to parse from address from email.")
        return ""

    def __parse_text_body_from_eml(self, eml):
        result = []
        try:
            msg = email.message_from_string(eml)
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    print("Found text/plain part '%s'.") % part.get_payload()
                    result.append(part.get_payload())
        except Exception as e:
            msg = "Error parsing message." + str(e)
            print(msg)
            result.append(msg)

        return result

    def __generate_message_file(self, from_adx, txt_body, url):
        return "From: '%s'\n\nBody: '%s'\n\nOriginal Email: '%s'" % (from_adx, txt_body, url)

    def __upload_txt_body_to_dropbox(self, raw_eml_data):
        from_adx = self.__parse_from_eml(raw_eml_data)
        plain_text_parts = self.__parse_text_body_from_eml(raw_eml_data)
        print(plain_text_parts)
        txt_body = "\n\n".join(plain_text_parts)
        url = self.__generate_self_signed_url(self.bucket, self.key)

        data = self.__generate_message_file(from_adx, txt_body, url)
        file_name = "/" + self.name + ".txt"
        print("Uploading txt '%s' to dropbox file '%s'.") % (data, file_name)
        self.__upload_data_to_dropbox(data, file_name)

    def process(self):
        name = self.__generate_name()

        print("Processing key '%s' in bucket '%s' in region '%s' with name '%s'.") % (self.key, self.bucket, self.region, self.name)
        raw_eml_data = self.__download_s3_object()

        self.__upload_txt_body_to_dropbox(raw_eml_data)
        print("Processing key '%s' in bucket '%s' in region '%s' as name '%s' complete.") % (self.key, self.bucket, self.region, self.name)
