# coding: utf-8
import boto3
# Establishing a Session.
session=boto3.Session(profile_name='python_automation')
# S3 Session
s3 = session.resource('s3')
# Creating a New Bucket
new_bucket_name = 'py-automation-proj'
bucket_region = 'us-west-1'
new_bucket = s3.create_bucket(Bucket=new_bucket_name, CreateBucketConfiguration={'LocationConstraint':bucket_region})
# Cheacking all buv
print([x for x in s3.buckets.all()])
