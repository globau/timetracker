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
        for entry in logs:
            print(
                "%s %s %s"
                % (entry.dt.format("HH:mm:ss"), entry.state.upper(), entry.reason)
            )
    else:
        print("(empty)")
