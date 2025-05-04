import importlib
from enum import Enum, IntEnum

from discord import Embed, User

from db.models.playerModel import PlayerModel


class StrListEnum(list[str], Enum):
  """Custom Enum for lists of strings."""

  pass


class EmbedColors(IntEnum):
  """Enum of color codes for Discord Embeds."""

  ERROR = 0x992D22
  DEFAULT = 0x2C2F33


class EmbedText(StrListEnum):
  """Enum of string lists for Embed text."""

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
  """Discord Embed for Exceptions."""

  def __init__(self, title: str, desc: str) -> None:
    super().__init__(
      color=EmbedColors.ERROR,
      title=title,
      description=desc,
    )


class HelpEmbed(Embed):
  """Discord Embed for Help command."""

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


class ProfileEmbed(Embed):
  """Discord Embed for Profile command."""

  def __init__(
    self,
    player: PlayerModel,
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
      value=f'**Level**: {player.stats["level"]}\n**XP**: {player.stats["currentxp"]}/{player.stats["requiredxp"]}',
      inline=False,
    )
    self.add_field(
      name='STATS',
      value=f':heart: **HP**: {player.stats["hp"]}/{player.stats["maxhp"]}\n:brain: **SAN**: {player.stats["san"]}/{player.stats["maxsan"]}\n:dagger: **ATK**: {player.stats["atk"]}\n:shield: **DEF**: {player.stats["dfs"]}\n*Use `/stats` for more.*',
      inline=True,
    )
    self.add_field(
      name='VALUABLES',
      value=f':coin: **Tokens**: {player.tokens}\n:candle: **Favour**: {player.favor}',
      inline=True,
    )
    self.set_footer(text=f'Playing since {date}')


class StatsEmbed(Embed):
  """Discord Embed for Stats command."""

  def __init__(self, player: PlayerModel, user: User):
    super().__init__(
      color=EmbedColors.DEFAULT,
      title='ALL STATS',
      description=f':heart: **Health**: {player.stats["hp"]}/{player.stats["maxhp"]}\n :brain: **Sanity**: {player.stats["san"]}/{player.stats["maxsan"]}\n :dagger: **Attack**: {player.stats["atk"]}\n :shield: **Defense**: {player.stats["dfs"]}\n :bulb: **Resistance**: {player.stats["rst"]}\n :eye: **Perception**: {player.stats["per"]}\n :footprints: **Stealth**: {player.stats["sth"]}',
    )
    self.set_author(
      name=f'{user.name} - stats',
      icon_url=user.display_avatar.url,
    )


class InventoryEmbed(Embed):
  """Discord Embed for Inventory command."""

  def __init__(self, player: PlayerModel):
    inventory = ''
    if (
      player.inventory is None or len(player.inventory) <= 0
    ):
      inventory = 'Your inventory is empty.'
    else:
      for key in player.inventory.keys():
        # Get the item
        ItemClass = getattr(
          importlib.import_module('core.items'), key
        )
        item = ItemClass()

        inventory = (
          inventory
          + f'**{item.name}**: {player.inventory[key]}\n'
        )

    super().__init__(
      color=EmbedColors.DEFAULT,
      title='INVENTORY',
      description=f'{inventory}',
    )


class CooldownsEmbed(Embed):
  """Discord Embed for Cooldowns command."""

  def __init__(self, cooldowns: dict):
    cooldowns_string = ''
    for key in cooldowns.keys():
      if cooldowns[key] == 'Ready':
        cooldowns_string = (
          cooldowns_string
          + f':white_check_mark: `/{key}`: {cooldowns[key]}\n'
        )
      else:
        cooldowns_string = (
          cooldowns_string
          + f':watch: `/{key}`: {cooldowns[key]}\n'
        )

    super().__init__(
      color=EmbedColors.DEFAULT,
      title='COOLDOWNS',
      description=cooldowns_string,
    )


# endregion
