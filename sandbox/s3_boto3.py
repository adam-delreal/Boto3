import boto3, botocore, click

# Establishing Session
prof_name = 'python_automation'
session = boto3.Session(profile_name=prof_name)

# Establishing Resources: S3
s3=session.resource('s3')

# Leverage click to work within the CLI
@click.group()
def cli():
    """
    Project which manages aws.
    """
    pass

# List Buckets
@cli.command('list-buckets')
def list_buckets():
    """
    Lists all S3 Buckets.
    """
    return [bucket for bucket in s3.buckets.all()]

# List Objects
@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """
    Lists objects within an S3 Bucket.
    """
    return [obj for obj in s3.Bucket(bucket).objects.all()]



if __name__ == '__main__':
    cli()
