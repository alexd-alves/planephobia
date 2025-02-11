import discord

from utility import EmbedColors


# Unidentified Exceptions
class ExceptionEmbed(discord.Embed):
  def __init__(self, extras='', display=True):
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


# Warnings
class WarningEmbed(discord.Embed):
  def __init__(self, title, description, extras='', display=False):
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
  def __init__(self):
    super().__init__(
      title='Not Registered',
      description='Register using `/start` to start playing!.',
    )


class ExistingPlayerEmbed(WarningEmbed):
  def __init__(self):
    super().__init__(
      title='Existing Player',
      description='You have already registered! Use `/profile` to see your details.',
    )


class ValidationErrorEmbed(WarningEmbed):
  def __init__(self, extras, display):
    super().__init__(
      title='Validation Error',
      description='Encountered a **pydantic `Validation Error`**. Check the data models match the existing DB entries.',
      extras=extras,
      display=display,
    )


class TypeErrorEmbed(WarningEmbed):
  def __init__(self, extras, display):
    super().__init__(
      title='Type Error',
      description='Response does not match expected Type.',
      extras=extras,
      display=display,
    )


# Player Profile
class ProfileEmbed(discord.Embed):
  def __init__(self, player, stats, user, date):
    super().__init__(
      color=EmbedColors.DEFAULT,
      title=player.title,
      description='Class here?',
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
  def __init__(self, stats, user):
    super().__init__(
      color=EmbedColors.DEFAULT,
      title='ALL STATS',
      description=f':heart: **Health**: {stats.hp}/{stats.maxhp}\n :brain: **Sanity**: {stats.san}/{stats.maxsan}\n :dagger: **Attack**: {stats.atk}\n :shield: **Defense**: {stats.dfs}\n :bulb: **Resistance**: {stats.rst}\n :eye: **Perception**: {stats.per}\n :footprints: **Stealth**: {stats.sth}',
    )
    self.set_author(
      name=f'{user.name} - stats', icon_url=user.display_avatar.url
    )
