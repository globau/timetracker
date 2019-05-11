import state
import ui
from main import cli


@cli.command(aliases=["a"], help="set away now")
def away():
    state.set_away(away=True, reason="requested")
    ui.notify(away=True)
