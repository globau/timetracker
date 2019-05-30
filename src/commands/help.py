from main import cli, click


@cli.command(aliases=["h"], hidden=True)
@click.argument("command", required=False)
def help(command=None):
    cli([command, "--help"] if command else ["--help"])
