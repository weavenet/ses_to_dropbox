import json
import os
import unittest

from record import Record

class BodyStub1():
    def read(self):
        return open("./test_data/valid1.eml").read()

class S3ClientStub1():
    def generate_presigned_url(self, **kwargs):
        return "https://s3/a-url"

    def get_object(self, **kwargs):
        if ((kwargs.get("Key") != "key") or (kwargs.get("Bucket") != "bucket")):
            raise Exception("Invalid key or bucket")

        return { "Body": BodyStub1() }

class DropboxStub():
    def __init__(self, stub):
        self.stub = stub

    def files_upload(self, data, file_name):
        if file_name.endswith(".eml"):
            if (data != (self.stub.read())):
                raise Exception("Received wrong email data: '%s' expects '%s'." % (data, BodyStub1().read()))
            return

        if file_name.endswith(".txt"):
            if (data.startswith("From: 'Test Sender <test@sender.com>'\n\nBody: 'hi user") != True):
                raise Exception("Received wrong text data: '%s'." % data)

            if (data.endswith("Original Email: 'https://s3/a-url'") != True):
                raise Exception("Received wrong text data: '%s'." % data)
            return

class TestRun(unittest.TestCase):
    def setUp(self):
        os.environ["DROPBOX_ACCESS_TOKEN"] = "test1234"

    def test1(self):
        record = Record("key", "bucket", "region")
        record.client = S3ClientStub1()
        record.dbx = DropboxStub(BodyStub1())
        record.process()

if __name__ == '__main__':
    unittest.main()
