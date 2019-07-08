# Boto3

## About
**Python script leveraging Boto3 to Automate AWS through the CLI.**
- Deploys, configures, lists, and creates snapshots of EC2 Instances & S3 Buckets.
- Work in Progress. Currently adding more functionality for S3.

## Configurations
Configuration via AWS CLI is needed.

```
aws configure --profile <profile-name>
```

## Running the Script

```
pipenv run "python Boto3/boto3_script.py <command> <--project=<project-name>>"
```

*commands*: list, start, stop, etc.

*project*: project name is optional.
