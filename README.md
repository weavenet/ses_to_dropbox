# ses_to_dropbox

If your like me, you have random domains from which you still want to receive emails.

This repo will allow you to setup AWS SES to receive emails for those domains (which is cheap),
and have a summary placed in Dropbox, via an AWS Lambda function (so you get an alert), with
a link to the full email in S3.

## Deploy

Tested with **Python 2.7**.

### Create Bucket and Function

* Create a [Dropbox app and oauth token](https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/).

* Create cloud formation template via the AWS console and provide the token created above.

### Deploy Updated Code

* Setup your virutal env:

```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

* Deploy the code the created functions

```
bash scripts/deploy.sh us-west-2
```

Update your SES rule to place the object in the S3 bucket (directions [here](http://docs.aws.amazon.com/ses/latest/DeveloperGuide/receiving-email-action-s3.html)).

## Test

```shell
python test.py
```
