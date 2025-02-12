import random
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from pydantic import ValidationError

import core.player as player
import core.titles as titles
import utility.embeds as embeds
from db.models.playerModels import Player, Stats
from db.routes import addPlayer, getPlayerByDiscordId

worship_dance_outcomes = {
  'You fail miserably, do you even know where left and right are? You have upset GhostKai.\nYou get -5 Favour.': -5,
  'You look ridiculous, but at least you managed to stay on your feet. However, GhostKai has standards.\n You get -1 Favour.': -1,
  'Mediocre, but it will have to do.\nYou get +1 Favour!': 1,
  'Your dance is adequate, GhostKai is pleased.\nYou get +3 Favour!': 3,
  'The light of our Lord GhostKai shines upon you! Your dance has greatly pleased Him.\nYou get +5 Favour!': 5,
}


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
        embed=embeds.ExistingPlayerEmbed()
      )
    else:
      newStats = Stats(
        level=1,
        currentxp=0,
        requiredxp=100,
        maxhp=10,
        maxsan=5,
        hp=10,
        atk=1,
        dfs=1,
        san=5,
        rst=1,
        per=1,
        sth=1,
      )
      newPlayer = Player(
        discord_id=interaction.user.id,
        title=titles.PlayerTitles._0,
        stats=newStats,
        tokens=100,
        favor=100,
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
            embed=embeds.ValidationErrorEmbed(
              extras=' * **`player.py: 79`:** `playerObject` is of Type `ValidationError`.',
              display=True,
            )
          )
      except Exception as e:
        return await interaction.response.send_message(
          embed=embeds.ExceptionEmbed(extras=e)
        )
    else:
      try:
        playerObject = await getPlayerByDiscordId(
          req, discord_id=interaction.user.id
        )
        if playerObject is ValidationError:
          return await interaction.response.send_message(
            embed=embeds.ValidationErrorEmbed(
              extras=' * **`player.py/profile(default user) - getPlayerByDiscordId()`:** `playerObject` is of Type `ValidationError`.',
              display=True,
            )
          )
      except Exception as e:
        return await interaction.response.send_message(
          embed=embeds.ExceptionEmbed(extras=e)
        )

    # Player Not Found
    if not playerObject:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Get discord user to be able to display name and avatar
    discordUser = self.bot.get_user(playerObject.discord_id)

    # Get stats and correctly formatted date
    playerStats = playerObject.stats
    registrationDate = playerObject.registered_at.strftime('%x')

    return await interaction.response.send_message(
      embed=embeds.ProfileEmbed(
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
          embed=embeds.ValidationErrorEmbed(
            extras=' * **`player.py/stats(default user) - getPlayerByDiscordId()`:** `playerObject` is of Type `ValidationError`.',
            display=True,
          )
        )
    except Exception as e:
      return await interaction.response.send_message(
        embed=embeds.ExceptionEmbed(extras=e)
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
      embed=embeds.StatsEmbed(
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
          embed=embeds.ValidationErrorEmbed(
            extras=' * **`player.py/worship - getPlayerByDiscordId()`:** `playerObject` is of Type `ValidationError`.',
            display=True,
          )
        )
    except Exception as e:
      return await interaction.response.send_message(
        embed=embeds.ExceptionEmbed(extras=e)
      )

    if type.value == 'dance':
      dance_result = random.choices(
        list(worship_dance_outcomes.keys())
      )
      dance_result = dance_result[0]

      # Calculate XP using gaussian distribution
      xp_mu = playerObject.stats.level * 25
      xp_sigma = playerObject.stats.level * 5
      xp_result = int(random.gauss(xp_mu, xp_sigma))

      try:
        await player.update_favor(
          req=req,
          player=playerObject,
          amount=worship_dance_outcomes.get(dance_result),
        )
        levelled_up = await player.update_xp(
          req=req,
          player=playerObject,
          amount=xp_result,
        )
      except Exception as e:
        return await interaction.response.send_message(
          embed=embeds.ExceptionEmbed(extras=e)
        )

      await interaction.response.send_message(
        'You try to perform the Kitty Dance...'
      )
      response = await interaction.original_response()
      if levelled_up:
        return await interaction.followup.edit_message(
          message_id=response.id,
          content=f'{response.content}\n{dance_result}\nYou also gain {xp_result} XP.\nYou have levelled up!',
        )
      return await interaction.followup.edit_message(
        message_id=response.id,
        content=f'{response.content}\n{dance_result}\nYou also gain {xp_result} XP.',
      )


async def setup(bot: commands.Bot):
  await bot.add_cog(PlayerCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
