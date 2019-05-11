import database
import ui
from main import cli, click


@click.argument("date", required=False, default="today")
@cli.command(aliases=["l"], help="logs for a day")
def log(date):
    dt = ui.parse_date(date, context="day")

    print(dt.format("ddd Do MMM"))
    logs = database.logs(dt)
    if logs:
        for l in logs:
            print("%s %s %s" % (l.dt.format("HH:mm:ss"), l.state.upper(), l.reason))
    else:
        print("(empty)")
