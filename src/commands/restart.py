from main import cli


@cli.command(help="restart daemon")
def restart():
    import launchd

    launchd.restart()
