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
from db.models.playerModels import Player
from db.routes import (
  addPlayer,
  getPlayerByDiscordId,
)


class PlayerCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.req = bot.app
    self.bot = bot

  # region Start
  @app_commands.command(
    name='start', description='Create a Player Profile.'
  )
  async def start(self, interaction: discord.Interaction):
    player = await getPlayerByDiscordId(
      self.req, discord_id=interaction.user.id
    )
    if player:
      await interaction.response.send_message(
        'You are already registered!'
      )
    else:
      view = buttons.PlayerClassButtons()
      await interaction.response.send_message(
        'Choose a class by pressing the buttons.', view=view
      )
      view.response = await interaction.original_response()
      await view.wait()

      if view.value == 'a':
        newPlayer = Player(
          discord_id=interaction.user.id,
          title=titles.PlayerTitles._0,
          playerClass='Test Class A',
          stats=playerClasses.defaultStatsA,
          tokens=100,
          favor=100,
          cooldowns=playerClasses.defaultCooldowns,
          registered_at=datetime.now(),
        )
        addedPlayer = await addPlayer(
          self.req, player=newPlayer
        )
        await interaction.followup.send(
          f'Added player: {addedPlayer}'
        )

      elif view.value == 'b':
        newPlayer = Player(
          discord_id=interaction.user.id,
          title=titles.PlayerTitles._0,
          playerClass='Test Class B',
          stats=playerClasses.defaultStatsB,
          tokens=100,
          favor=100,
          cooldowns=playerClasses.defaultCooldowns,
          registered_at=datetime.now(),
        )
        addedPlayer = await addPlayer(
          self.req, player=newPlayer
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
        playerObject = await getPlayerByDiscordId(
          self.req, discord_id=user.id
        )
        if playerObject is ValidationError:
          raise playerObject
      except Exception as e:
        raise e
    # If not given, query for caller
    else:
      try:
        playerObject = await getPlayerByDiscordId(
          self.req, discord_id=interaction.user.id
        )
        if playerObject is ValidationError:
          raise playerObject
      except Exception as e:
        raise e

    # Player Not Found in DB
    if not playerObject:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Get discord user to be able to display name and avatar
    discordUser = self.bot.get_user(playerObject.discord_id)

    # Get stats and correctly formatted date
    playerStats = playerObject.stats
    registrationDate = playerObject.registered_at.strftime(
      '%x'
    )

    return await interaction.response.send_message(
      embed=embeds.ProfileEmbed(
        player=playerObject,
        stats=playerStats,
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
      playerObject = await getPlayerByDiscordId(
        self.req, discord_id=interaction.user.id
      )
      if playerObject is ValidationError:
        raise playerObject
    except Exception as e:
      raise e

    # Player Not Found
    if not playerObject:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Get discord user to be able to display name and avatar
    discordUser = self.bot.get_user(playerObject.discord_id)

    # Get stats
    playerStats = playerObject.stats

    return await interaction.response.send_message(
      embed=embeds.StatsEmbed(
        stats=playerStats,
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


async def setup(bot: commands.Bot):
  await bot.add_cog(PlayerCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
