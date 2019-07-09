import boto3, botocore, click

# Establishing Session
prof_name = 'python_automation'
session = boto3.Session(profile_name=prof_name)

# Establishing Resources: EC2 & S3
ec2=session.resource('ec2')
s3=session.resource('s3')

# Leverage click to work within the CLI
@click.group()
def cli():
    """
    Project which manages aws.
    """
    pass


# Adding command: "volume"
@cli.group('volumes')
def volumes():
    """
    Commands used for volumes.
    """
    pass


# Adding command: "instances"
@cli.group('instances')
def instances():
    """
    Commands used for instances.
    """
    pass

###################### EC2 ######################
def filter_instances(project):
    """
    Filters EC2 instances according to project name.
    """
    instances = []
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances=ec2.instances.filter(Filters=filters)
    else:
        instances=ec2.instances.all()
    return instances


def has_pending_snapshot(volume):
    """
    States whether a snapshot is pending.
    """
    snapshot=list(volume.snapshot.all())
    return snapshot and snapshot[0].state == 'pending'


@snapshots.command('list')
@click.option('--project',
              default=None,
              help='Only snapshots for project (tag project:<name>)')
@click.option('--all', 'list_all',
              default=False,
              is_flag=True,
              help='List all snapshots for each volume, not the most recent')
def list_snapshots(project, list_all):
    """
    Lists EC2 Snapshots
    """
    instances=filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time_strftime("%c")
                )))
                if s.state == 'completed' and not list_all: break
    return


@volumes.command('list')
@click.option('--project',
              default=None,
              help='Only volumes for project (tag project:<name>)')
def list_volumes(project):
    """
    Lists EC2 Volumes
    """
    instances=filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return


@instances.command('snapshot',
                   help='Create snapshots of all volumes')
@click.option('--project',
              default=None,
              help='Only instances forproject (tag project: <name>)')
def create_snapshot(project):
    """
    Creates Snapshots for EC2 instances
    """
    for i in instances:
        print(f"Stopping {i.id}...")
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print(f' Skipping {v.id}, snapshot already in progress')
                continue
            print('Creating snapshot of {v.id}')
            v.create_snapshot(Description='Created by snapshot function.')
        print(f"Starting {i.id}...")
        i.start()
        i.wait_until_running()
    print("Jobs are done!")
    return


@instances.command('list')
@click.option('--project',
              default=None,
              help='Only instance for project (tag project:<name>)')
def list_instances(project):
    """
    Lists EC2 instances
    """
    instances=filter_instances(project)
    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
            )))
    return

@instances.command('stop')
@click.option('--project',
              default=None,
              help='Only instances for the project')
def stop_instances(project):
    """
    Stops EC2 Instances
    """
    instances=filter_instances(project)
    for i in instances:
        print(f"Stopping {i.id}...")
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(f"Cloud could not stop {i.id}. " + str(e))
            continue
    return


@instances.command('start')
@click.option('--project', default=None,
  help='Only instances for the project')
def start_instances(project):
    """
    Starts EC2 Instances
    """
    instances=filter_instances(project)
    for i in instances:
        print(f"Starting {i.id}...")
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(f"Cloud could not start {i.id}. " + str(e))
            continue
    return


########################## S3 #############################
@cli.command('list-buckets')
def list_buckets():
    """
    Lists all S3 Buckets.
    """
    return [bucket for bucket in s3.buckets.all()]


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """
    Lists objects within an S3 Bucket.
    """
    return [obj for obj in s3.Bucket(bucket).objects.all()]


###### CURRENTLY WORKING ON:
@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """
    Create and Configures an S3 Bucket.
    """
    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={'LocationConstraints':session.region_name}
            )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyCreated':
            s3_bucket = s3.Bucket(bucket)
        else:
            raise e


if __name__ == '__main__':
    cli()
