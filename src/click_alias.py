import click


class ClickAliasedGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aliases = {}
        self._commands = {}

    def command(self, *args, **kwargs):
        aliases = kwargs.pop("aliases", [])
        decorator = super().command(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._aliases[cmd.name] = aliases
                for alias in aliases:
                    self._commands[alias] = cmd.name
            return cmd

        return _decorator

    def get_command(self, ctx, cmd_name):
        # resolve alias --> command name
        return super().get_command(ctx, self._commands.get(cmd_name, cmd_name))

    def format_commands(self, ctx, formatter):
        # (ab)use formatter to inject aliases into help description
        assert isinstance(formatter, click.HelpFormatter)

        formatter._aliases = self._aliases  # pylint: disable=protected-access

        formatter.__class__ = AliasFormatter
        super().format_commands(ctx, formatter)
        formatter.__class__ = click.HelpFormatter


# noinspection PyUnresolvedReferences
class AliasFormatter(click.HelpFormatter):
    def write_dl(self, rows, col_max=30, col_spacing=2):
        # pylint: disable=no-member
        new_rows = []
        for row in rows:
            name, help_msg = row
            if self._aliases.get(name):
                name = "%s (%s)" % (name, ",".join(self._aliases[name]))
            new_rows.append((name, help_msg))

        super().write_dl(new_rows, col_max=col_max, col_spacing=col_spacing)
