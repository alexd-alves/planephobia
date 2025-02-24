from enum import IntEnum

import discord

from db.models.playerModels import Player, Stats


class EmbedColors(IntEnum):
  ERROR = 0x992D22
  WARNING = 0xA84300
  DEFAULT = 0x2C2F33


# region Exceptions
class ExceptionEmbed(discord.Embed):
  def __init__(self, extras: str = '', display: bool = True) -> None:
    if not display:
      super().__init__(
        color=EmbedColors.ERROR,
        title='Error',
        description='Exception Encountered',
      )
    else:
      super().__init__(
        color=EmbedColors.ERROR, title='Error', description=extras
      )


# endregion


# region Warnings
class WarningEmbed(discord.Embed):
  def __init__(
    self,
    title: str,
    description: str,
    extras: str = '',
    display: bool = False,
  ) -> None:
    if not display:
      super().__init__(
        color=EmbedColors.WARNING,
        title=title,
        description=description,
      )
    if display:
      description = description + '\n' + extras
      super().__init__(
        color=EmbedColors.WARNING,
        title=title,
        description=description,
      )


class NotRegisteredEmbed(WarningEmbed):
  def __init__(self) -> None:
    super().__init__(
      title='Not Registered',
      description='Register using `/start` to start playing!.',
    )


class ExistingPlayerEmbed(WarningEmbed):
  def __init__(self) -> None:
    super().__init__(
      title='Existing Player',
      description='You have already registered! Use `/profile` to see your details.',
    )


class ValidationErrorEmbed(WarningEmbed):
  def __init__(self, extras: str, display: bool) -> None:
    super().__init__(
      title='Validation Error',
      description='Encountered a **pydantic `Validation Error`**. Check the data models match the existing DB entries.',
      extras=extras,
      display=display,
    )


class TypeErrorEmbed(WarningEmbed):
  def __init__(self, extras: str, display: bool):
    super().__init__(
      title='Type Error',
      description='Response does not match expected Type.',
      extras=extras,
      display=display,
    )


# endregion


# region Basic Commands
# Help
help_dev = [
  '* `/sync`: Re-sync all commands globally.',
  '* `/reload`: Reload an extension after changes. Use to avoid restarting application after command changes.',
]
help_test = [
  '* `/yeet`: Delete a Player on DB to force restart.',
  '  - `user`: Player to Yeet.',
  '* `/items`: Shows all available items.',
  '  - `type`: Optional',
]
help_basic = [
  '* `/profile`: Display Player profile.',
  '  - `user` (Optional).',
  '* `/stats`: Display full Player stats.',
  '* `/worship`: Worship our Lord GhostKai to obtain his Favour.',
  '  - `type`: You can perform the following types of activities to worship:',
  '    * `dance`: Perform the Kitty dance.',
  '* `/duel`: Challenge another player to a duel.',
  '  - `type`: The following types of duels are available:',
  '    * `dice`: Player who rolls the higher number on a D20 wins.',
  '    * `dice hardcore`: Same as dice but no XP is awarded on ties and loser loses XP too.',
  '  - `target`: Another player.',
]


class HelpEmbed(discord.Embed):
  def __init__(self):
    super().__init__(
      color=EmbedColors.DEFAULT,
      title='Planephobia Commands',
    )
    self.add_field(
      name='Getting Started',
      value='* `/start`: Registers Player.',
      inline=False,
    )
    self.add_field(
      name='Developer Only', value='\n'.join(help_dev), inline=False
    )
    self.add_field(
      name='Testing Commands',
      value='\n'.join(help_test),
      inline=False,
    )
    self.add_field(
      name='Basic Commands',
      value='\n'.join(help_basic),
      inline=False,
    )


# endregion


# region Player Commands
# Player Profile
class ProfileEmbed(discord.Embed):
  def __init__(
    self, player: Player, stats: Stats, user: discord.User, date: str
  ):
    super().__init__(
      color=EmbedColors.DEFAULT,
      title=player.title,
      description=player.playerClass,
    )
    self.set_author(
      name=f'{user.name} - profile', icon_url=user.display_avatar.url
    )
    self.set_thumbnail(url=user.display_avatar.url)
    self.add_field(
      name='PROGRESS',
      value=f'**Level**: {stats.level}\n**XP**: {stats.currentxp}/{stats.requiredxp}',
      inline=False,
    )
    self.add_field(
      name='STATS',
      value=f':heart: **HP**: {stats.hp}/{stats.maxhp}\n:brain: **SAN**: {stats.san}/{stats.maxsan}\n:dagger: **ATK**: {stats.atk}\n:shield: **DEF**: {stats.dfs}\n*Use `/stats` for more.*',
      inline=True,
    )
    self.add_field(
      name='VALUABLES',
      value=f':coin: **Tokens**: {player.tokens}\n:candle: **Favour**: {player.favor}',
      inline=True,
    )
    self.set_footer(text=f'Playing since {date}')


# Stats Embed
class StatsEmbed(discord.Embed):
  def __init__(self, stats: Stats, user: discord.User):
    super().__init__(
      color=EmbedColors.DEFAULT,
      title='ALL STATS',
      description=f':heart: **Health**: {stats.hp}/{stats.maxhp}\n :brain: **Sanity**: {stats.san}/{stats.maxsan}\n :dagger: **Attack**: {stats.atk}\n :shield: **Defense**: {stats.dfs}\n :bulb: **Resistance**: {stats.rst}\n :eye: **Perception**: {stats.per}\n :footprints: **Stealth**: {stats.sth}',
    )
    self.set_author(
      name=f'{user.name} - stats', icon_url=user.display_avatar.url
    )


# endregion
