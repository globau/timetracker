import database
from main import cli


@cli.command(help="check database consistency")
def check():
    database.consistency_check()
