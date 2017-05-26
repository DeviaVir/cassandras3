import click
from .backup import backup_cmd
from .restore import restore_cmd
from .list import list_cmd

commands = (backup_cmd, restore_cmd, list_cmd)
cli = click.CommandCollection(sources=commands)
