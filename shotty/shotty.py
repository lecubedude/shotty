import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instance=[]

    if project:
        filters = [{'Name': 'tag:Name', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def as_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots.state[0] == 'pending'


@click.group()
def cli():
    """Shotty snapshot management"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshotss with tag Name:<name>")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each EC2 volume")
def list_snapshots(project, list_all):   
    "List EC2 volume snapshots"

    instances = filter_instances(project)

    for i in instances: 
        for v in i.volumes.all(): 
            for s in v.snapshots.all(): 
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                if s.state == "completed" and not list_all: break

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes with tag Name:<name>")
def list_volumes(project):   
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances: 
        for v in i.volumes.all(): 
            print(", ".join(( 
                v.id, 
                i.id, 
                v.state, 
                str(v.size) + "GB", 
                v.encrypted and "Encrypted" or "Not Encrypted" 
            )))

    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot',
    help="Only instances with tag Name:<name>")
@click.option('--project', default=None,
    help="Create snapshots of all EC2 volumes")

def create_snapshots(project):   
    "Create EC2 volume snapshots"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id)) 
        
        i.stop()
        i.wait_until_stopped()
        
        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print("skipping {0}, snapshot already in progress".format(v.id))
                continue

            print("   Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created bu shotty")
        print("Starting {0}...".format(i.id))
        
        i.start()
        i.wait_until_running()

    print("Job is done!")

    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances with tag Name:<name>")
def list_instances(project):   
    "List EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Name', '<no project>')
            )))
    return

@instances.command('stop')
@click.option('--project', default=None,
    help='Only instances with tag Name:<name>')
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)
    
    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None,
    help='Only instances with tag Name:<name>')
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)
    
    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not start {0}. ".format(i.id) + str(e))
            continue

    return

if __name__ == '__main__':
    cli()
