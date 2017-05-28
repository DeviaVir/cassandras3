![Build Status](https://travis-ci.org/DeviaVir/cassandras3.svg)

# cassandras3
A simple tool to help you backup and restore your cassandra data to and from S3.

## Setup

### AWS

This utility assumes you have correctly set up a (local) credentials file (via e.g. `aws configure`), it is also possible to pass credentials using the CLI environment variables:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

The recommended way is to give nodes that run the backups permissions to the bucket via their instance profiles to execute PUT commands. When restoring a backup, we can use a separate user which will have GET permissions.

## Python (pip)

### Installation

On Debian-based systems, make sure you have installed the `python-pip` package.

```
pip install cassandras3
```

Or install manually:
```
git clone git@github.com:DeviaVir/cassandras3.git
cd cassandras3
python setup.py install
```

### Usage

Make sure `cassandra` is running, `nodetool` requires it.

#### Backup

```
cassandras3 backup --keyspace test --bucket test [--region us-east-1]
```

Note: `[--region us-east-1]` is optional, it is to cache the AWS client API's per region.

#### View

```
cassandras3 view --keyspace test --hostname test --bucket test [--region us-east-1]
```

This will return a list of all available backups to restore from.

Note: `[--region us-east-1]` is optional, it is to cache the AWS client API's per region.
Note: you do not need to specify the hostname, it is useful if you want to list backups from a different machine.

#### Restore

```
cassandras3 restore --backup backup-timestamp --hostname test --keyspace test --bucket test [--region us-east-1]
```

Note: `backup-timestamp` can be retrieved via `cassandras3 view`.
Note: `[--region us-east-1]` is optional, it is to cache the AWS client API's per region.
Note: this command assumes the data directories are currently empty, if this restore is executed over a currently running cluster it can behave unexpectedly.
Note: you do not need to specify the hostname, it is useful if you want to list backups from a different machine.


## Docker

You can use docker in case you are already currently using docker to deploy your cassandra nodes. This allows for easy linking.

### Installation

Simply run:

```
docker-compose build
```

And optionally push this to a public or private repository, from which every node that will be running this can pull the image from. (`docker pull [your-private-repository]/cassandras3:latest`)


### Usage

#### Backup

```
docker run -it \
	-v $HOME/.aws:/home/.aws \
	-v /var/lib/cassandra/data:/var/lib/cassandra/data \
	--link cassandra_node:cassandra \
	 cassandras3_app:latest backup --host cassandra --keyspace test --bucket test [--region us-east-1]
```

Note: the first mount (`-v`) expects AWS to be configured correctly on the host machine. The mount is not necessary when using instance profiles.
Note: `[--region us-east-1]` is optional, it is to cache the AWS client API's per region.

#### List

```
docker run -it \
	-v $HOME/.aws:/home/.aws \
	cassandras3_app:latest view --keyspace test --hostname test --bucket test [--region us-east-1]
```

Note: the first mount (`-v`) expects AWS to be configured correctly on the host machine. The mount is not necessary when using instance profiles.
Note: you do not need to specify the hostname, it is useful if you want to list backups from a different machine.
Note: `[--region us-east-1]` is optional, it is to cache the AWS client API's per region.

#### Restore

```
docker run -it \
	-v $HOME/.aws:/home/.aws \
	-v /var/lib/cassandra/data:/var/lib/cassandra/data \
	--link cassandra_node:cassandra \
	cassandras3_app:latest restore --host cassandra --hostname test --keyspace test --bucket test [--region us-east-1]
```

Note: you do not need to specify the hostname, it is useful if you want to restore a backup from a different machine.
Note: the first mount (`-v`) expects AWS to be configured correctly on the host machine. The mount is not necessary when using instance profiles.
Note: this command assumes the data directories are currently empty, if this restore is executed over a currently running cluster it can behave unexpectedly.
Note: `[--region us-east-1]` is optional, it is to cache the AWS client API's per region.

## Development

To easily develop locally without the need for docker:

```
cd ~/into/the/project/directory
make clean build/venv
source build/venv/bin/activate
cd src
python -m cassandras3.main
```

### Deploy new pip versions

Requires a correctly set up `~/.pypirc`.

Testing:
```
python setup.py sdist upload -r pypitest
```

Live:
```
python setup.py sdist upload -r pypi
```
