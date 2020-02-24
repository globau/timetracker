from main import cli, click, invoke


@cli.command(name="help", aliases=["h"], hidden=True)
@click.argument("command", required=False)
def help_cmd(command=None):
    invoke([command, "--help"] if command else ["--help"])
