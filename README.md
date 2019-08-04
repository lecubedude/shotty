# shotty
Simple AWS Snapshot app in python3
Let's do this!!

## About

This project is a simple demo using boto3 to manage AWS EC2 snapshots.

## Config

shotty uses the aws cli configuration file using profile called 'shotty' to access EC2 resources.
you need to either create a shotty IAM user, or edit the shotty.py file to update the aws profile
to use an IAM user you already have setup.

aws configure --profile shotty


# Running the code

'pipenv run "python [path]/shotty.py <command> <subcommand>
<--project=PROJECT>"'

# Command Options

commands are:
instances
volumes
snapshots

subcommands are:
list
create
start
stop