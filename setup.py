from setuptools import setup

setup(
    name='snap-shotty',
    version='0.1',
    author='Ian Evans',
    author_email='lecube@icloud.com',
    description='snap-shotty is a simple tool that will list and create snapshots for EC2 instances',
    license='GPLv3+',
    packages=['shotty'],
    url='https://github.com/lecubedude/shotty',
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    '''
)
