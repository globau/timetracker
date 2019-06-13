from main import cli, click, invoke


@cli.command(aliases=["h"], hidden=True)
@click.argument("command", required=False)
def help(command=None):
    invoke([command, "--help"] if command else ["--help"])
