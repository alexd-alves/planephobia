import random
import traceback
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from pydantic import ValidationError

from core import enemies, player
from db.models.playerModels import Cooldowns, Player
from db.routes import getPlayerByDiscordId, updatePlayer
from utility import buttons, embeds

# region Settings
COOLDOWN_CMDS = ['worship', 'duel', 'hunt']
COOLDOWN_TIMES = {'worship': 3, 'duel': 0, 'hunt': 1}

WORSHIP_DANCE_OUTCOMES = {
  'You fail miserably, do you even know where left and right are? You have upset GhostKai.\nYou get -5 Favour.': -5,
  'You look ridiculous, but at least you managed to stay on your feet. However, GhostKai has standards.\n You get -1 Favour.': -1,
  'Mediocre, but it will have to do.\nYou get +1 Favour!': 1,
  'Your dance is adequate, GhostKai is pleased.\nYou get +3 Favour!': 3,
  'The light of our Lord GhostKai shines upon you! Your dance has greatly pleased Him.\nYou get +5 Favour!': 5,
}
WORSHIP_DANCE_WEIGHTS = [5, 10, 40, 35, 10]
# endregion


class ActionsCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.req = bot.app

  # !! Keep Cooldowns command here to avoid global consts

  # region Cooldowns
  @app_commands.command(
    name='cooldowns',
    description='All command cooldowns.',
  )
  async def cooldowns(
    self, interaction: discord.Interaction
  ) -> None:
    # Query database for player
    try:
      playerObject: Player = await getPlayerByDiscordId(
        self.req, discord_id=interaction.user.id
      )
      if playerObject is ValidationError:
        raise playerObject
    except Exception as e:
      raise e

    # Player Not Found on DB
    if not playerObject:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Get cooldowns
    playerCooldowns: Cooldowns = playerObject.cooldowns
    # Filter out special methods and create dict
    remainingDeltas: dict[str, str] = {}
    # Get all time diffs and update to None if exceeded
    for attr in COOLDOWN_CMDS:
      timestamp = getattr(playerCooldowns, attr)
      if timestamp:
        timeSince = (
          datetime.now(timezone.utc).timestamp() - timestamp
        )
        timeRemaining = (
          COOLDOWN_TIMES.get(attr) * 60
        ) - timeSince
        if timeRemaining <= 0:
          setattr(playerCooldowns, attr, None)
          remainingDeltas[attr] = 'Ready'
        else:
          minutes, seconds = divmod(timeRemaining, 60)
          hours, minutes = divmod(minutes, 60)
          remainingDeltas[attr] = '%d:%02d:%02d' % (
            hours,
            minutes,
            seconds,
          )
      else:
        remainingDeltas[attr] = 'Ready'

    # Update player in DB to remove nulled cooldowns
    playerObject.cooldowns = playerCooldowns
    try:
      await player.batch_update_cooldowns(
        self.req, playerObject
      )
    except Exception as e:
      raise e

    return await interaction.response.send_message(
      remainingDeltas
    )

  @cooldowns.error
  async def cooldowns_error(
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
        'Error in "cooldowns" (actions_cog.py)', desc
      )
    )

  # endregion

  # region Worship
  @app_commands.command(
    name='worship',
    description='Worship our Lord GhostKai to try to win some favor.',
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
    # Get player from db
    try:
      playerObject: Player = await getPlayerByDiscordId(
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

    # Check Cooldown
    cooldown: str | None = (
      playerObject.cooldowns.cooldown_by_name(
        COOLDOWN_TIMES, 'worship', playerObject
      )
    )
    if cooldown:
      return await interaction.response.send_message(
        cooldown
      )

    # region Dance
    if type.value == 'dance':
      # Choose result based on given weights
      dance_result: list[str] = random.choices(
        list(WORSHIP_DANCE_OUTCOMES.keys()),
        WORSHIP_DANCE_WEIGHTS,
      )
      dance_result: str = dance_result[0]

      # Calculate XP
      xp_result: int = playerObject.calculate_xp_gauss(
        25, 5
      )

      try:
        # Update Favor and XP
        await player.update_favor(
          req=self.req,
          player=playerObject,
          amount=WORSHIP_DANCE_OUTCOMES.get(dance_result),
        )
        # If XP meets Required XP, levelled_up contains how many levels
        levelled_up: int | None = await player.update_xp(
          req=self.req,
          player=playerObject,
          amount=xp_result,
        )
        # Reset the Cooldown
        await player.start_cooldown(
          self.req, playerObject, 'worship'
        )
      except Exception as e:
        raise e

      # Respond to Player
      await interaction.response.send_message(
        f'**{interaction.user.display_name}** tries to perform the ***Kitty Dance***...'
      )
      # Get original response to edit
      response = await interaction.original_response()
      if levelled_up:
        return await interaction.followup.edit_message(
          message_id=response.id,
          content=f'{response.content}\n{dance_result}\nYou also gain {xp_result} XP.\nYou have levelled up {levelled_up} times!',
        )
      return await interaction.followup.edit_message(
        message_id=response.id,
        content=f'{response.content}\n{dance_result}\nYou also gain {xp_result} XP.',
      )
    # endregion

  @worship.error
  async def worship_error(
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
        'Error in "worship" (actions_cog.py)', desc
      )
    )

  # endregion

  # region Duel
  @app_commands.command(
    name='duel', description='Fight other players 1v1.'
  )
  @app_commands.describe(
    type='What do you want to challenge your Target to?',
    target='The User you want to duel.',
  )
  @app_commands.choices(
    type=[
      app_commands.Choice(name='dice', value='dice'),
      app_commands.Choice(
        name='dice hardcore', value='dice hardcore'
      ),
    ]
  )
  async def duel(
    self,
    interaction: discord.Interaction,
    type: app_commands.Choice[str],
    target: discord.Member,
  ):
    # Prevent user from tagging themselves
    if interaction.user.id == target.id:
      return await interaction.response.send_message(
        'You cannot challenge yourself to a duel.'
      )

    # Get both players from db
    try:
      initPlayer: Player = await getPlayerByDiscordId(
        self.req, discord_id=interaction.user.id
      )
      targetPlayer: Player = await getPlayerByDiscordId(
        self.req, discord_id=target.id
      )
      if initPlayer is ValidationError:
        raise initPlayer
      if targetPlayer is ValidationError:
        raise targetPlayer
    except Exception as e:
      raise e

    # Player Not Found in DB
    if not initPlayer:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Target Not Found in DB
    if not targetPlayer:
      return await interaction.response.send_message(
        "Target Player doesn't exist or isn't registered."
      )

    # Check cooldown for initiator
    cooldown: str | None = (
      initPlayer.cooldowns.cooldown_by_name(
        COOLDOWN_TIMES, 'duel'
      )
    )
    if cooldown:
      return await interaction.response.send_message(
        cooldown
      )

    # Check cooldown for target
    cooldown: str | None = (
      targetPlayer.cooldowns.cooldown_by_name(
        COOLDOWN_TIMES, 'duel', target.name
      )
    )
    if cooldown:
      return await interaction.response.send_message(
        cooldown
      )

    # region Dice

    if type.value == 'dice':
      # Set up the Duel Buttons
      view = buttons.DuelConsentButton(
        init=interaction.user.id,
        target=target.id,
      )
      await interaction.response.send_message(
        f"{interaction.user.name} has challenged {target.name} to a dice duel!\nDo you accept **{interaction.user.name}**'s challenge, {target.mention}?",
        view=view,
      )
      view.response = await interaction.original_response()
      await view.wait()

      # If Duel Accepted
      if view.value:
        # Update Cooldowns
        try:
          await player.start_cooldown(
            self.req, initPlayer, 'duel'
          )
          await player.start_cooldown(
            self.req, targetPlayer, 'duel'
          )
        except Exception as e:
          raise e

        # Roll the Dice
        initPlayerRoll: int = random.randint(1, 20)
        targetPlayerRoll: int = random.randint(1, 20)

        # If result is a Tie
        if initPlayerRoll == targetPlayerRoll:
          # Calculate XPs (both players get half multiplier)
          init_xp: int = initPlayer.calculate_xp_gauss(
            25, 5
          )
          target_xp: int = targetPlayer.calculate_xp_gauss(
            25, 5
          )

          # Update XPs
          try:
            # Initiator
            init_levelled_up: (
              int | None
            ) = await player.update_xp(
              req=self.req,
              player=initPlayer,
              amount=init_xp,
            )
            # Target
            target_levelled_up: (
              int | None
            ) = await player.update_xp(
              req=self.req,
              player=targetPlayer,
              amount=target_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f"{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\nIt's a tie!"
          )

          # Follow up with initiator XP
          if init_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP. You level up {init_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP.'
            )

          # Then target XP
          if target_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.name} gains {init_xp} XP. You level up {init_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.name} gains {init_xp} XP.'
            )

        # If Initiator Wins
        elif initPlayerRoll > targetPlayerRoll:
          # Calculate XP
          init_xp: int = initPlayer.calculate_xp_gauss(
            50, 5
          )

          # Update XP
          try:
            init_levelled_up: (
              int | None
            ) = await player.update_xp(
              req=self.req,
              player=initPlayer,
              amount=init_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\n**{interaction.user.name}** wins!'
          )

          # Follow up with XP
          if init_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP. {interaction.user.name} levels up {init_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP.'
            )

        # If Target Wins
        elif targetPlayerRoll > initPlayerRoll:
          # Calculate XP using gaussian distribution
          target_xp: int = targetPlayer.calculate_xp_gauss(
            50, 5
          )

          # Update XP
          try:
            target_levelled_up: (
              int | None
            ) = await player.update_xp(
              req=self.req,
              player=targetPlayer,
              amount=target_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\n**{target.name}** wins!'
          )

          # Follow up with XP
          if target_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{target.name} gains {target_xp} XP. {target.name} levels up {target_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{target.name} gains {target_xp} XP.'
            )

    # endregion

    # region Dice Hardcore
    elif type.value == 'dice hardcore':
      # Set up the Duel Buttons
      view = buttons.DuelConsentButton(
        init=interaction.user.id,
        target=target.id,
      )
      await interaction.response.send_message(
        f"{interaction.user.name} has challenged {target.name} to a Hardcore Dice duel!\nDo you accept **{interaction.user.name}**'s challenge, {target.mention}?",
        view=view,
      )
      view.response = await interaction.original_response()
      await view.wait()

      # If Duel Accepted
      if view.value:
        # Update Cooldowns
        try:
          await player.start_cooldown(
            self.req, initPlayer, 'duel'
          )
          await player.start_cooldown(
            self.req, targetPlayer, 'duel'
          )
        except Exception as e:
          raise e

        # Roll the Dice
        initPlayerRoll: int = random.randint(1, 20)
        targetPlayerRoll: int = random.randint(1, 20)

        # If result is a Tie
        if initPlayerRoll == targetPlayerRoll:
          # No one earns XP, send result
          followup = await interaction.followup.send(
            f"{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\nIt's a tie! No one gets anything."
          )

        # If Initiator wins
        elif initPlayerRoll > targetPlayerRoll:
          # Calculate Initiator's XP win
          init_xp: int = initPlayer.calculate_xp_gauss(
            50, 5
          )

          # Calculate XP loss for target
          target_xp: int = (
            targetPlayer.calculate_xp_gauss(50, 5) * -1
          )

          # Update XPs
          try:
            init_levelled_up: (
              int | None
            ) = await player.update_xp(
              req=self.req,
              player=initPlayer,
              amount=init_xp,
            )
            target_levelled_up: (
              int | None
            ) = await player.update_xp(
              req=self.req,
              player=targetPlayer,
              amount=target_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\n**{interaction.user.name}** wins!'
          )

          # Follow up with Initiator XP win
          if init_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP. {interaction.user.name} levels up {init_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP.'
            )

          # Then Target XP loss
          followup = await followup.edit(
            content=f'{followup.content}\n{target.name} loses {target_xp * -1} XP.'
          )

        # If Target wins
        elif targetPlayerRoll > initPlayerRoll:
          # Calculate Target XP win
          target_xp: int = targetPlayer.calculate_xp_gauss(
            50, 5
          )

          # Calculate Initiator's loss
          init_xp: int = (
            initPlayer.calculate_xp_gauss(50, 5) * -1
          )

          # Update XPs
          try:
            target_levelled_up: (
              int | None
            ) = await player.update_xp(
              req=self.req,
              player=targetPlayer,
              amount=target_xp,
            )
            init_levelled_up: (
              int | None
            ) = await player.update_xp(
              req=self.req,
              player=initPlayer,
              amount=init_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\n**{target.name}** wins!'
          )

          # Follow up with Target XP win
          if target_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{target.name} gains {target_xp} XP. {target.name} levels up {target_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{target.name} gains {target_xp} XP.'
            )

          # Then Initiator XP loss
          followup = await followup.edit(
            content=f'{followup.content}\n{interaction.user.name} loses {init_xp * -1} XP.'
          )

    # endregion

  @duel.error
  async def duel_error(
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
        'Error in "duel" (actions_cog.py)', desc
      )
    )

  # endregion

  # region Hunt
  @app_commands.command(
    name='hunt', description='Hunt small mobs.'
  )
  async def hunt(self, interaction: discord.Interaction):
    # Get Player from DB
    try:
      playerObject: Player = await getPlayerByDiscordId(
        self.req, discord_id=interaction.user.id
      )
      if playerObject is ValidationError:
        raise playerObject
    except Exception as e:
      raise e

    # Check Cooldown
    cooldown: str | None = (
      playerObject.cooldowns.cooldown_by_name(
        COOLDOWN_TIMES, 'hunt', playerObject
      )
    )
    if cooldown:
      return await interaction.response.send_message(
        cooldown
      )

    # Update Cooldown
    try:
      await player.start_cooldown(
        self.req, playerObject, 'hunt'
      )
    except Exception as e:
      raise e

    enemy = enemies.Redvelvet()
    initialhp: int = playerObject.stats.hp

    # Player takes turn first
    while playerObject.stats.hp > 0 and enemy.hp > 0:
      # Player's turn
      enemy.hp = enemy.hp - playerObject.stats.atk
      # Enemy's turn
      if enemy.hp > 0:
        playerObject.stats.hp = int(
          playerObject.stats.hp
          - (
            enemy.atk * (80 / 100 + playerObject.stats.dfs)
          )
        )

    if playerObject.stats.hp > 0:
      # Calculate XP using gaussian distribution
      xp_result: int = playerObject.calculate_xp_gauss(
        35, 5
      )

      # Update XP and HP
      try:
        # HP First
        await updatePlayer(
          self.req, playerObject.id, playerObject
        )

        # Then XP
        levelled_up: int | None = await player.update_xp(
          req=self.req,
          player=playerObject,
          amount=xp_result,
        )
      except Exception as e:
        raise e

      if levelled_up:
        return await interaction.response.send_message(
          f'**{interaction.user.name}** found and killed a {enemy.name.upper()}.\nGained {xp_result} XP and lost {initialhp - playerObject.stats.hp} HP. Remaining HP is {playerObject.stats.hp}/{playerObject.stats.maxhp}.\nYou level up {levelled_up} times!'
        )
      else:
        return await interaction.response.send_message(
          f'**{interaction.user.name}** found and killed a {enemy.name.upper()}.\nGained {xp_result} XP and lost {initialhp - playerObject.stats.hp} HP. Remaining HP is {playerObject.stats.hp}/{playerObject.stats.maxhp}.'
        )
    else:
      return await interaction.response.send_message(
        f'**{interaction.user.name}** found a {enemy.name.upper()} and died fighting it.'
      )


# endregion


async def setup(bot: commands.Bot):
  await bot.add_cog(ActionsCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
