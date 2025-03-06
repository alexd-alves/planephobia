from enum import Enum, IntEnum

from discord import Embed, User

from db.models.playerModels import Player, Stats


class StrListEnum(list[str], Enum):
  pass


class EmbedColors(IntEnum):
  ERROR = 0x992D22
  DEFAULT = 0x2C2F33


class EmbedText(StrListEnum):
  HELP_DEV = [
    '* `/sync`: Re-sync all commands globally.',
    '* `/reload`: Reload an extension after changes. Use to avoid restarting application after command changes.',
  ]
  HELP_TEST = [
    '* `/yeet`: Delete a Player from DB to force restart.',
    '  - `user`: Player to Yeet.',
    '* `/items`: Shows all available Items.',
    '  - `type`: (Optional) Display only a specific category of Items.',
  ]
  HELP_BASIC = [
    '* `/start`: Register with the bot to play.',
    '* `/profile`: Display Player Profile with abridged Stats.',
    '  - `user` (Optional) See another Profile.',
    '* `/stats`: Display full Player stats.',
    '* `/cooldowns`: Display all Command Cooldowns.',
    '* `/worship`: Worship our Lord GhostKai to win his Favor.',
    '  - `type`: You can perform the following types of activities to worship:',
    '    * `dance`: Perform the Kitty dance.',
    '* `/duel`: Challenge another player to a duel.',
    '  - `type`: The following types of duels are available:',
    '    * `dice`: Player who rolls the higher number on a D20 wins.',
    '    * `dice hardcore`: Same as dice but no XP is awarded on ties and loser loses XP too.',
    '  - `target`: Another player.',
    '* `/hunt`: Fight a Mob.',
  ]


class ExceptionEmbed(Embed):
  def __init__(self, title: str, desc: str) -> None:
    super().__init__(
      color=EmbedColors.ERROR,
      title=title,
      description=desc,
    )


class HelpEmbed(Embed):
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
      name='Developer Only',
      value='\n'.join(EmbedText.HELP_DEV),
      inline=False,
    )
    self.add_field(
      name='Testing Commands',
      value='\n'.join(EmbedText.HELP_TEST),
      inline=False,
    )
    self.add_field(
      name='Basic Commands',
      value='\n'.join(EmbedText.HELP_BASIC),
      inline=False,
    )


# region Player Commands


# Player Profile
class ProfileEmbed(Embed):
  def __init__(
    self,
    player: Player,
    stats: Stats,
    user: User,
    date: str,
  ):
    super().__init__(
      color=EmbedColors.DEFAULT,
      title=player.title,
      description=player.playerClass,
    )
    self.set_author(
      name=f'{user.name} - profile',
      icon_url=user.display_avatar.url,
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
class StatsEmbed(Embed):
  def __init__(self, stats: Stats, user: User):
    super().__init__(
      color=EmbedColors.DEFAULT,
      title='ALL STATS',
      description=f':heart: **Health**: {stats.hp}/{stats.maxhp}\n :brain: **Sanity**: {stats.san}/{stats.maxsan}\n :dagger: **Attack**: {stats.atk}\n :shield: **Defense**: {stats.dfs}\n :bulb: **Resistance**: {stats.rst}\n :eye: **Perception**: {stats.per}\n :footprints: **Stealth**: {stats.sth}',
    )
    self.set_author(
      name=f'{user.name} - stats',
      icon_url=user.display_avatar.url,
    )


# endregion
