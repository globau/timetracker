import state
import ui
from main import cli


@cli.command(aliases=["b"], help="set back now")
def back():
    state.set_away(back=True, reason="requested")
    ui.notify(back=True)
