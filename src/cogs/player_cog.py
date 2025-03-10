import traceback
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from pydantic import ValidationError

import core.titles as titles
import utility.buttons as buttons
import utility.embeds as embeds
import utility.playerClasses as playerClasses
from db.models.playerModel import PlayerModel
from db.routes import add_player, get_player


class PlayerCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.app = bot.app
    self.bot = bot

  # region Start
  @app_commands.command(
    name='start', description='Create a Player Profile.'
  )
  async def start(self, interaction: discord.Interaction):
    # Initialize player
    player = None
    try:
      player = await get_player(
        self.app, discord_id=interaction.user.id
      )
    except Exception:
      pass
    if player:
      return await interaction.response.send_message(
        'You are already registered!'
      )
    # else:
    view = buttons.PlayerClassButtons()
    await interaction.response.send_message(
      'Choose a class by pressing the buttons.', view=view
    )
    view.response = await interaction.original_response()
    await view.wait()

    if view.value == 'a':
      newPlayer = PlayerModel(
        discord_id=interaction.user.id,
        title=titles.PlayerTitles._0,
        playerClass='Test Class A',
        stats=playerClasses.defaultStatsA,
        tokens=100,
        favor=100,
        cooldowns=playerClasses.defaultCooldowns,
        registered_at=datetime.now(),
      )
      addedPlayer = await add_player(
        self.app, player=newPlayer
      )
      await interaction.followup.send(
        f'Added player: {addedPlayer}'
      )

    elif view.value == 'b':
      newPlayer = PlayerModel(
        discord_id=interaction.user.id,
        title=titles.PlayerTitles._0,
        playerClass='Test Class B',
        stats=playerClasses.defaultStatsB,
        tokens=100,
        favor=100,
        cooldowns=playerClasses.defaultCooldowns,
        registered_at=datetime.now(),
      )
      addedPlayer = await add_player(
        self.app, player=newPlayer
      )
      await interaction.followup.send(
        f'Added player: {addedPlayer}'
      )

  @start.error
  async def start_error(
    self,
    interaction: discord.Interaction,
    error: commands.CommandError,
  ):
    if isinstance(
      error, app_commands.errors.CommandNotFound
    ):
      return
    if isinstance(
      error, app_commands.errors.CommandInvokeError
    ):
      if isinstance(error.original, ValidationError):
        desc = 'ValidationError'
      else:
        error_data = ''.join(
          traceback.format_exception(
            type(error), error, error.__traceback__
          )
        )
        desc = f'Unknown Exception raised via CommandInvokeError:\n```py\n{error_data[:1000]}\n```'
    elif isinstance(
      error, app_commands.errors.BotMissingPermissions
    ):
      desc = f'I am missing required permissions:\n{", ".join(error.missing_permissions)}'
    elif isinstance(
      error, app_commands.errors.MissingPermissions
    ):
      desc = f'You are missing required permissions:\n{", ".join(error.missing_permissions)}'
    else:
      error_data = ''.join(
        traceback.format_exception(
          type(error), error, error.__traceback__
        )
      )
      desc = (
        f'Unknown error\n```py\n{error_data[:1000]}\n```'
      )
      print(error_data)
    return await interaction.response.send_message(
      embed=embeds.ExceptionEmbed(
        'Error in "start" (player_cog.py)', desc
      )
    )

  # endregion

  # region Profile
  @app_commands.command(
    name='profile',
    description='Your full Profile, with abridged Stats.',
  )
  @app_commands.describe(
    user="Look at someone else's profile."
  )
  async def profile(
    self,
    interaction: discord.Interaction,
    user: Optional[discord.Member],
  ) -> None:
    # Query database for Target player
    if user:
      try:
        player: PlayerModel = PlayerModel(
          **await get_player(self.app, discord_id=user.id)
        )
      except Exception as e:
        raise e
    # If not given, query for caller
    else:
      try:
        player: PlayerModel = PlayerModel(
          **await get_player(
            self.app, discord_id=interaction.user.id
          )
        )
      except Exception as e:
        raise e

    # Get discord user to be able to display name and avatar
    discordUser = self.bot.get_user(player.discord_id)

    # Get stats and correctly formatted date
    registrationDate = player.registered_at.strftime('%x')

    return await interaction.response.send_message(
      embed=embeds.ProfileEmbed(
        player=player,
        user=discordUser,
        date=registrationDate,
      )
    )

  @profile.error
  async def profile_error(
    self,
    interaction: discord.Interaction,
    error: commands.CommandError,
  ):
    if isinstance(
      error, app_commands.errors.CommandNotFound
    ):
      return
    if isinstance(
      error, app_commands.errors.CommandInvokeError
    ):
      if isinstance(error.original, ValidationError):
        desc = 'ValidationError'
      else:
        error_data = ''.join(
          traceback.format_exception(
            type(error), error, error.__traceback__
          )
        )
        desc = f'Unknown Exception raised via CommandInvokeError:\n```py\n{error_data[:2500]}\n```'
    elif isinstance(
      error, app_commands.errors.BotMissingPermissions
    ):
      desc = f'I am missing required permissions:\n{", ".join(error.missing_permissions)}'
    elif isinstance(
      error, app_commands.errors.MissingPermissions
    ):
      desc = f'You are missing required permissions:\n{", ".join(error.missing_permissions)}'
    else:
      error_data = ''.join(
        traceback.format_exception(
          type(error), error, error.__traceback__
        )
      )
      desc = (
        f'Unknown error\n```py\n{error_data[:1000]}\n```'
      )
      print(error_data)
    return await interaction.response.send_message(
      embed=embeds.ExceptionEmbed(
        'Error in "profile" (player_cog.py)', desc
      )
    )

  # endregion

  # region Stats
  @app_commands.command(
    name='stats', description='Your full Stats.'
  )
  async def stats(
    self, interaction: discord.Interaction
  ) -> None:
    # Query database for player
    try:
      player = PlayerModel(
        **await get_player(
          self.app, discord_id=interaction.user.id
        )
      )
    except Exception as e:
      raise e

    # Player Not Found
    if not player:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Get discord user to be able to display name and avatar
    discordUser = self.bot.get_user(player.discord_id)

    return await interaction.response.send_message(
      embed=embeds.StatsEmbed(
        player=player,
        user=discordUser,
      )
    )

  @stats.error
  async def stats_error(
    self,
    interaction: discord.Interaction,
    error: commands.CommandError,
  ):
    if isinstance(
      error, app_commands.errors.CommandNotFound
    ):
      return
    if isinstance(
      error, app_commands.errors.CommandInvokeError
    ):
      if isinstance(error.original, ValidationError):
        desc = 'ValidationError'
      else:
        error_data = ''.join(
          traceback.format_exception(
            type(error), error, error.__traceback__
          )
        )
        desc = f'Unknown Exception raised via CommandInvokeError:\n```py\n{error_data[:1000]}\n```'
    elif isinstance(
      error, app_commands.errors.BotMissingPermissions
    ):
      desc = f'I am missing required permissions:\n{", ".join(error.missing_permissions)}'
    elif isinstance(
      error, app_commands.errors.MissingPermissions
    ):
      desc = f'You are missing required permissions:\n{", ".join(error.missing_permissions)}'
    else:
      error_data = ''.join(
        traceback.format_exception(
          type(error), error, error.__traceback__
        )
      )
      desc = (
        f'Unknown error\n```py\n{error_data[:1000]}\n```'
      )
      print(error_data)
    return await interaction.response.send_message(
      embed=embeds.ExceptionEmbed(
        'Error in "stats" (_cog.py)', desc
      )
    )

  # endregion

  # region Inventory
  @app_commands.command(
    name='inventory', description='Your items.'
  )
  async def inventory(
    self, interaction: discord.Interaction
  ) -> None:
    # Query database for player
    try:
      player = PlayerModel(
        **await get_player(
          self.app, discord_id=interaction.user.id
        )
      )
    except Exception:
      raise

    return await interaction.response.send_message(
      embed=embeds.InventoryEmbed(player=player)
    )

  @inventory.error
  async def inventory_error(
    self,
    interaction: discord.Interaction,
    error: commands.CommandError,
  ):
    if isinstance(
      error, app_commands.errors.CommandNotFound
    ):
      return
    if isinstance(
      error, app_commands.errors.CommandInvokeError
    ):
      if isinstance(error.original, ValidationError):
        desc = 'ValidationError'
      else:
        error_data = ''.join(
          traceback.format_exception(
            type(error), error, error.__traceback__
          )
        )
        desc = f'Unknown Exception raised via CommandInvokeError:\n```py\n{error_data[:1000]}\n```'
    elif isinstance(
      error, app_commands.errors.BotMissingPermissions
    ):
      desc = f'I am missing required permissions:\n{", ".join(error.missing_permissions)}'
    elif isinstance(
      error, app_commands.errors.MissingPermissions
    ):
      desc = f'You are missing required permissions:\n{", ".join(error.missing_permissions)}'
    else:
      error_data = ''.join(
        traceback.format_exception(
          type(error), error, error.__traceback__
        )
      )
      desc = (
        f'Unknown error\n```py\n{error_data[:1000]}\n```'
      )
      print(error_data)
    return await interaction.response.send_message(
      embed=embeds.ExceptionEmbed(
        'Error in "stats" (_cog.py)', desc
      )
    )

  # endregion


async def setup(bot: commands.Bot):
  await bot.add_cog(PlayerCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
