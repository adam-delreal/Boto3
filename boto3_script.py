import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2=session.resource('ec2')

def filter_instances(project):
  instances = []
  if project:
    filters = [{'Name':'tag:Project', 'Values':[project]}]
    instances=ec2.instances.filter(Filters=filters)
  else:
    instances=ec2.instances.all()
  return instances

def has_pending_snapshot(volume):
	snapshot=list(volume.snapshot.all())
	return snapshot and snapshot[0].state == 'pending'


@click.group()
def cli():
	"""Project Repo manages snapshots"""

@cli.group('volumes')
def volumes():
  """Commands for volumes"""

@cli.group('instances')
def instances():
  """Commands for instances"""



@snapshots.command('list')
@click.option('--project', default=None,
  help='Only snapshots for project (tag project:<name>)')
@click.option('--all', 'list_all', default=False, is_flag=True,
						 help='List all snapshots for each volume, not the most recent')
def list_snapshots(project, list_all):
  "list EC2 Snapshots"
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
@click.option('--project', default=None,
  help='Only volumes for project (tag project:<name>)')
def list_volumes(project):
  "list EC2 volumes"
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



@instances.command('snapshot', help='Create snapshots of all volumes')
@click.option('--project', default=None,
						 help='Only instances forproject (tag project: <name>)')
def create_snapshot(project):
	"""Create snapshots for EC2 instances"""
	for i in instances:
		print("Stopping {0}...".format(i.id))
		i.stop()
		i.wait_until_stopped()
		for v in i.volumes.all():
			if has_pending_snapshot(v):
				print(' Skipping {0}, snapshot already in progress'.format(v.id))
				continue
			print('Creating snapshot of {0}'.format(v.id))
			v.create_snapshot(Description='Created by snapshot function.')
		print("Starting {0}...".format(i.id))
		i.start()
		i.wait_until_running()
	print("Jobs are done!")
	return



@instances.command('list')
@click.option('--project', default=None,
  help='Only instance for project (tag project:<name>)')
def list_instances(project):
  "list EC2 instances"
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
@click.option('--project', default=None,
  help='Only instances for the project')
def stop_instances(project):
  """Stop EC2 Instances"""
  instances=filter_instances(project)

  for i in instances:
    print("Stopping {0}...".format(i.id))
		try:
    	i.stop()
		except botocore.exceptions.ClientError as e:
			print("Cloud could not stop {0}. ".format(i.id) + str(e))
			continue
	return


@instances.command('start')
@click.option('--project', default=None,
  help='Only instances for the project')
def start_instances(project):
  """Start EC2 Instances"""
  instances=filter_instances(project)

  for i in instances:
    print("Starting {0}...".format(i.id))
    try:
    	i.start()
		except botocore.exceptions.ClientError as e:
			print("Cloud could not start {0}. ".format(i.id) + str(e))
			continue
	return


if __name__ == '__main__':
  cli()
