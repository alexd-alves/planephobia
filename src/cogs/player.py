import random
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from pydantic import ValidationError

from db.models.playerModels import Player
from db.routes import addPlayer, getPlayerByDiscordId, updatePlayer
from embeds import (
  ExceptionEmbed,
  ExistingPlayerEmbed,
  NotRegisteredEmbed,
  ProfileEmbed,
  StatsEmbed,
  ValidationErrorEmbed,
)
from titles import PlayerTitles


class PlayerCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

  # Start
  @app_commands.command(
    name='start', description='Registers the player.'
  )
  async def start(self, interaction: discord.Interaction):
    req = self.bot.app
    player = await getPlayerByDiscordId(
      req, discord_id=interaction.user.id
    )
    if player:
      await interaction.response.send_message(
        embed=ExistingPlayerEmbed()
      )
    else:
      newPlayer = Player(
        discord_id=interaction.user.id,
        title=PlayerTitles._0,
        stats={
          'level': 1,
          'currentxp': 0,
          'requiredxp': 100,
          'maxhp': 10,
          'hp': 10,
          'atk': 1,
          'dfs': 1,
          'san': 5,
          'rst': 1,
          'per': 1,
          'sth': 1,
        },
        tokens=100,
        registered_at=datetime.now(),
      )
      addedPlayer = await addPlayer(req, player=newPlayer)
      await interaction.response.send_message(
        f'Added player: {addedPlayer}'
      )

  # Profile
  @app_commands.command(
    name='profile', description='Displays the player profile.'
  )
  async def profile(
    self,
    interaction: discord.Interaction,
    user: Optional[discord.Member],
  ) -> None:
    req = self.bot.app

    # Initialize PlayerObject
    playerObject = None

    # Query database for player
    if user:
      try:
        playerObject = await getPlayerByDiscordId(
          req, discord_id=user.id
        )
        if playerObject is ValidationError:
          return await interaction.response.send_message(
            embed=ValidationErrorEmbed(
              extras=' * **`player.py: 79`:** `playerObject` is of Type `ValidationError`.',
              display=True,
            )
          )
      except Exception as e:
        return await interaction.response.send_message(
          embed=ExceptionEmbed(extras=e)
        )
    else:
      try:
        playerObject = await getPlayerByDiscordId(
          req, discord_id=interaction.user.id
        )
        if playerObject is ValidationError:
          return await interaction.response.send_message(
            embed=ValidationErrorEmbed(
              extras=' * **`player.py/profile(default user) - getPlayerByDiscordId()`:** `playerObject` is of Type `ValidationError`.',
              display=True,
            )
          )
      except Exception as e:
        return await interaction.response.send_message(
          embed=ExceptionEmbed(extras=e)
        )

    # Player Not Found
    if not playerObject:
      return await interaction.response.send_message(
        embed=NotRegisteredEmbed()
      )

    # Get discord user to be able to display name and avatar
    discordUser = self.bot.get_user(playerObject.discord_id)

    # Get stats and correctly formatted date
    playerStats = playerObject.stats
    registrationDate = playerObject.registered_at.strftime('%x')

    return await interaction.response.send_message(
      embed=ProfileEmbed(
        player=playerObject,
        stats=playerStats,
        user=discordUser,
        date=registrationDate,
      )
    )

  # Stats
  @app_commands.command(
    name='stats', description='Display full player stats.'
  )
  async def stats(self, interaction: discord.Interaction) -> None:
    req = self.bot.app

    # Initialize PlayerObject
    playerObject = None

    # Query database for player
    try:
      playerObject = await getPlayerByDiscordId(
        req, discord_id=interaction.user.id
      )
      if playerObject is ValidationError:
        return await interaction.response.send_message(
          embed=ValidationErrorEmbed(
            extras=' * **`player.py/stats(default user) - getPlayerByDiscordId()`:** `playerObject` is of Type `ValidationError`.',
            display=True,
          )
        )
    except Exception as e:
      return await interaction.response.send_message(
        embed=ExceptionEmbed(extras=e)
      )

    # Player Not Found
    if not playerObject:
      return await interaction.response.send_message(
        embed=NotRegisteredEmbed()
      )

    # Get discord user to be able to display name and avatar
    discordUser = self.bot.get_user(playerObject.discord_id)

    # Get stats
    playerStats = playerObject.stats

    return await interaction.response.send_message(
      embed=StatsEmbed(
        stats=playerStats,
        user=discordUser,
      )
    )

  # Worship
  @app_commands.command(
    name='worship', description='Worship our lord GhostKai!'
  )
  @app_commands.choices(
    type=[
      app_commands.Choice(name='dance', value='dance'),
    ]
  )
  async def worship(
    self,
    interaction: discord.Interaction,
    type: app_commands.Choice[str],
  ):
    req = self.bot.app

    # Get player from db
    try:
      playerObject = await getPlayerByDiscordId(
        req, discord_id=interaction.user.id
      )
      if playerObject is ValidationError:
        return await interaction.response.send_message(
          embed=ValidationErrorEmbed(
            extras=' * **`player.py/worship - getPlayerByDiscordId()`:** `playerObject` is of Type `ValidationError`.',
            display=True,
          )
        )
    except Exception as e:
      return await interaction.response.send_message(
        embed=ExceptionEmbed(extras=e)
      )

    if type.value == 'dance':
      outcomes = [
        'You fail miserably, do you even know where left and right are? You have upset GhostKai.\nYou get -5 Favour.',
        'You look ridiculous, but at least you managed to stay on your feet. However, GhostKai has standards.\n You get -1 Favour.',
        'Mediocre, but it will have to do.\nYou get +1 Favour!',
        'Your dance is adequate, GhostKai is pleased.\nYou get +3 Favour!',
        'The light of our Lord GhostKai shines upon you! Your dance has greatly pleased Him.\nYou get +5 Favour!',
      ]

      # Choose outcome
      result = random.choices(outcomes, weights=(5, 20, 35, 30, 10))
      result = result[0]

      # Add favor to existing
      index = outcomes.index(result)
      if index == 0:
        playerObject.favor = playerObject.favor - 5
      elif index == 1:
        playerObject.favor = playerObject.favor - 1
      elif index == 2:
        playerObject.favor = playerObject.favor + 1
      elif index == 3:
        playerObject.favor = playerObject.favor + 3
      elif index == 4:
        playerObject.favor = playerObject.favor + 5

      # Add XP
      playerObject.stats.currentxp = playerObject.stats.currentxp + 10

      # Update DB
      try:
        await updatePlayer(
          req, id=playerObject.id, player=playerObject
        )
      except Exception as e:
        return await interaction.response.send_message(
          embed=ExceptionEmbed(extras=e)
        )

      await interaction.response.send_message(
        'You try to perform the Kitty Dance...'
      )
      response = await interaction.original_response()
      return await interaction.followup.edit_message(
        message_id=response.id,
        content=f'{response.content}\n{result}',
      )


async def setup(bot: commands.Bot):
  await bot.add_cog(PlayerCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
