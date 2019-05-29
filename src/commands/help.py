from main import cli


@cli.command(aliases=["h"], hidden=True)
def help():
    cli(["--help"])
