import click
from .backup import backup_cmd
from .restore import restore_cmd
from .view import view_cmd

CMDS = (backup_cmd, restore_cmd, view_cmd)
CLI = click.CommandCollection(sources=CMDS)
