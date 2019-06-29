# coding: utf-8
import boto3
# Establishing a Session.
session=boto3.Session(profile_name='python_automation')
s3 = session.resource('s3')

if __name__ == '__main__':
    # Printing buckets
    [print(x)for x in s3.buckets.all()]
