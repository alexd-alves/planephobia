import importlib
import random
import traceback
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from fastapi import HTTPException
from pydantic import ValidationError

import core.player_utils as utils
from db.models.playerModel import PlayerModel
from db.models.updatePlayerModel import UpdatePlayerModel
from db.routes import get_player, update_player
from utility import buttons, embeds

# region Settings
COOLDOWN_CMDS = ['worship', 'duel', 'hunt']
COOLDOWN_TIMES = {
  'worship': 0,  # 3
  'duel': 0,  # 10
  'hunt': 0,  # 1
}

WORSHIP_DANCE_OUTCOMES = {
  'You fail miserably, do you even know where left and right are? You have upset GhostKai.\nYou get -5 Favour.': -5,
  'You look ridiculous, but at least you managed to stay on your feet. However, GhostKai has standards.\n You get -1 Favour.': -1,
  'Mediocre, but it will have to do.\nYou get +1 Favour!': 1,
  'Your dance is adequate, GhostKai is pleased.\nYou get +3 Favour!': 3,
  'The light of our Lord GhostKai shines upon you! Your dance has greatly pleased Him.\nYou get +5 Favour!': 5,
}
WORSHIP_DANCE_WEIGHTS = [5, 10, 40, 35, 10]

HUNT_MOBS = {
  'Bundt': 0.15,
  'Redvelvet': 0.35,
  'CinnamonRoll': 0.5,
  'RedvelvetCupcake': 1.0,
}
# endregion


class ActionsCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.app = bot.app

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
      player: PlayerModel = await get_player(
        self.app, discord_id=interaction.user.id
      )
      print(player)
    except Exception as e:
      raise e

    # Player Not Found on DB
    if not player:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Get cooldowns
    player_cooldowns = player['cooldowns']
    # Filter out special methods and create dict
    remainingDeltas: dict[str, str] = {}
    # Get all time diffs and update to None if exceeded
    for attr in COOLDOWN_CMDS:
      timestamp = player_cooldowns[attr]
      if timestamp:
        timeSince = (
          datetime.now(timezone.utc).timestamp() - timestamp
        )
        timeRemaining = (
          COOLDOWN_TIMES.get(attr) * 60
        ) - timeSince
        if timeRemaining <= 0:
          player_cooldowns[attr] = None
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
    new_player = UpdatePlayerModel(
      cooldowns=player_cooldowns
    )
    try:
      await update_player(
        self.app, interaction.user.id, new_player
      )
    except Exception as e:
      raise e

    return await interaction.response.send_message(
      embed=embeds.CooldownsEmbed(remainingDeltas)
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
      elif isinstance(error.original, HTTPException):
        desc = f'HTTP Error {error.original.status_code}'
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
      player: PlayerModel = PlayerModel(
        **await get_player(
          self.app, discord_id=interaction.user.id
        )
      )
    except Exception as e:
      raise e

    # Player Not Found in DB
    if not player:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Check Cooldown
    cooldown: str | None = player.cooldown_by_name(
      COOLDOWN_TIMES, 'worship'
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
      xp_result: int = player.calculate_xp_gauss(25, 5)

      try:
        # Update Favor and XP
        await utils.update_favor(
          self.app,
          player,
          WORSHIP_DANCE_OUTCOMES.get(dance_result),
        )
        # If XP meets Required XP, levelled_up contains how many levels
        levelled_up: int | None = await utils.update_xp(
          self.app,
          player,
          xp_result,
        )
        # Reset the Cooldown
        await utils.start_cooldown(
          self.app, player, 'worship'
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
        if levelled_up == 1:
          return await interaction.followup.edit_message(
            message_id=response.id,
            content=f'{response.content}\n{dance_result}\nYou also gain {xp_result} XP.\nYou have levelled up {levelled_up} time!',
          )
        else:
          return await interaction.followup.edit_message(
            message_id=response.id,
            content=f'{response.content}\n{dance_result}\nYou also gain {xp_result} XP.\nYou have levelled up {levelled_up} time!',
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
      elif isinstance(error.original, HTTPException):
        desc = f'HTTP Error {error.original.status_code}'
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
      initiator: PlayerModel = PlayerModel(
        **await get_player(
          self.app, discord_id=interaction.user.id
        )
      )
      target: PlayerModel = PlayerModel(
        **await get_player(self.app, discord_id=target.id)
      )
    except Exception as e:
      raise e

    # Player Not Found in DB
    if not initiator:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Target Not Found in DB
    if not target:
      return await interaction.response.send_message(
        "Target Player doesn't exist or isn't registered."
      )

    # Check cooldown for initiator
    cooldown: str | None = initiator.cooldown_by_name(
      COOLDOWN_TIMES, 'duel'
    )
    if cooldown:
      return await interaction.response.send_message(
        cooldown
      )

    # Check cooldown for target
    cooldown: str | None = target.cooldown_by_name(
      COOLDOWN_TIMES, 'duel', target.name
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
          await utils.start_cooldown(
            self.app, initiator, 'duel'
          )
          await utils.start_cooldown(
            self.app, target, 'duel'
          )
        except Exception as e:
          raise e

        # Roll the Dice
        initiator_roll: int = random.randint(1, 20)
        target_roll: int = random.randint(1, 20)

        # If result is a Tie
        if initiator_roll == target_roll:
          # Calculate XPs (both players get half multiplier)
          init_xp: int = initiator.calculate_xp_gauss(25, 5)
          target_xp: int = target.calculate_xp_gauss(25, 5)

          # Update XPs
          try:
            # Initiator
            init_levelled_up: (
              int | None
            ) = await utils.update_xp(
              app=self.app,
              player=initiator,
              amount=init_xp,
            )
            # Target
            target_levelled_up: (
              int | None
            ) = await utils.update_xp(
              app=self.app,
              player=target,
              amount=target_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f"{interaction.user.name}: {initiator_roll}\n{target.name}: {target_roll}\nIt's a tie!"
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
        elif initiator_roll > target_roll:
          # Calculate XP
          init_xp: int = initiator.calculate_xp_gauss(50, 5)

          # Update XP
          try:
            init_levelled_up: (
              int | None
            ) = await utils.update_xp(
              app=self.app,
              player=initiator,
              amount=init_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initiator_roll}\n{target.name}: {target_roll}\n**{interaction.user.name}** wins!'
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
        elif target_roll > initiator_roll:
          # Calculate XP using gaussian distribution
          target_xp: int = target.calculate_xp_gauss(50, 5)

          # Update XP
          try:
            target_levelled_up: (
              int | None
            ) = await utils.update_xp(
              app=self.app,
              player=target,
              amount=target_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initiator_roll}\n{target.name}: {target_roll}\n**{target.name}** wins!'
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
          await utils.start_cooldown(
            self.app, initiator, 'duel'
          )
          await utils.start_cooldown(
            self.app, target, 'duel'
          )
        except Exception as e:
          raise e

        # Roll the Dice
        initiator_roll: int = random.randint(1, 20)
        target_roll: int = random.randint(1, 20)

        # If result is a Tie
        if initiator_roll == target_roll:
          # No one earns XP, send result
          followup = await interaction.followup.send(
            f"{interaction.user.name}: {initiator_roll}\n{target.name}: {target_roll}\nIt's a tie! No one gets anything."
          )

        # If Initiator wins
        elif initiator_roll > target_roll:
          # Calculate Initiator's XP win
          init_xp: int = initiator.calculate_xp_gauss(50, 5)

          # Calculate XP loss for target
          target_xp: int = (
            target.calculate_xp_gauss(50, 5) * -1
          )

          # Update XPs
          try:
            init_levelled_up: (
              int | None
            ) = await utils.update_xp(
              app=self.app,
              player=initiator,
              amount=init_xp,
            )
            target_levelled_up: (
              int | None
            ) = await utils.update_xp(
              app=self.app,
              player=target,
              amount=target_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initiator_roll}\n{target.name}: {target_roll}\n**{interaction.user.name}** wins!'
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
        elif target_roll > initiator_roll:
          # Calculate Target XP win
          target_xp: int = target.calculate_xp_gauss(50, 5)

          # Calculate Initiator's loss
          init_xp: int = (
            initiator.calculate_xp_gauss(50, 5) * -1
          )

          # Update XPs
          try:
            target_levelled_up: (
              int | None
            ) = await utils.update_xp(
              app=self.app,
              player=target,
              amount=target_xp,
            )
            init_levelled_up: (
              int | None
            ) = await utils.update_xp(
              app=self.app,
              player=initiator,
              amount=init_xp,
            )
          except Exception as e:
            raise e

          # Send result
          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initiator_roll}\n{target.name}: {target_roll}\n**{target.name}** wins!'
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
      elif isinstance(error.original, HTTPException):
        desc = f'HTTP Error {error.original.status_code}'
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
      player: PlayerModel = PlayerModel(
        **await get_player(
          self.app, discord_id=interaction.user.id
        )
      )
    except Exception as e:
      raise e

    # Check Cooldown
    cooldown: str | None = player.cooldown_by_name(
      COOLDOWN_TIMES, 'hunt'
    )
    if cooldown:
      return await interaction.response.send_message(
        cooldown
      )

    # Update Cooldown
    try:
      await utils.start_cooldown(self.app, player, 'hunt')
    except Exception as e:
      raise e

    # Pick a Mob
    mob = random.choices(
      list(HUNT_MOBS.keys()),
      cum_weights=list(HUNT_MOBS.values()),
    )
    # Instantiate the Mob
    EnemyClass = getattr(
      importlib.import_module('core.enemies'), mob[0]
    )
    enemy = EnemyClass()

    initial_player_hp: int = player.stats['hp']

    # Player takes turn first
    while player.stats['hp'] > 0 and enemy.hp > 0:
      # Player's turn
      enemy.hp = enemy.hp - player.stats['atk']
      # Enemy's turn
      if enemy.hp > 0:
        player.stats['hp'] = int(
          player.stats['hp']
          - (enemy.atk * (80 / 100 + player.stats['dfs']))
        )

    if player.stats['hp'] > 0:
      # Calculate XP
      xp_result: int = player.calculate_xp_gauss(35, 5)

      # Calculate loot
      available_loot = list(enemy.drops.keys())
      cum_weights = list(enemy.drops.values())

      # Add none as total cumulative weight
      available_loot.append('None')
      cum_weights.append(1.0)

      loot = random.choices(
        available_loot, cum_weights=cum_weights
      )

      if loot[0] != 'None':
        # Get the item
        ItemClass = getattr(
          importlib.import_module('core.items'), loot[0]
        )
        item = ItemClass()

        # Add the item to inventory
        await utils.add_item(
          self.app, player, loot[0], 1
        )  # TODO: varible amounts of loot?

      # Update XP and HP
      try:
        # HP
        new_player = UpdatePlayerModel(stats=player.stats)
        await update_player(
          self.app, player.discord_id, new_player
        )

        # Then XP
        levelled_up: int | None = await utils.update_xp(
          app=self.app,
          player=player,
          amount=xp_result,
        )
      except Exception as e:
        raise e

      if loot[0] != 'None':
        if levelled_up:
          return await interaction.response.send_message(
            f'**{interaction.user.name}** found and killed a {enemy.emoji}{enemy.name.upper()}.\nGained {xp_result} XP and lost {initial_player_hp - player.stats["hp"]} HP. Remaining HP is {player.stats["hp"]}/{player.stats["maxhp"]}:heart:.\nYou level up {levelled_up} times!\nReceived: {item.emoji}{item.name.upper()}.'
          )
        else:
          return await interaction.response.send_message(
            f'**{interaction.user.name}** found and killed a {enemy.emoji}{enemy.name.upper()}.\nGained {xp_result} XP and lost {initial_player_hp - player.stats["hp"]} HP. Remaining HP is {player.stats["hp"]}/{player.stats["maxhp"]}:heart:\nReceived: {item.emoji}{item.name.upper()}.'
          )
      else:
        if levelled_up:
          return await interaction.response.send_message(
            f'**{interaction.user.name}** found and killed a {enemy.emoji}{enemy.name.upper()}.\nGained {xp_result} XP and lost {initial_player_hp - player.stats["hp"]} HP. Remaining HP is {player.stats["hp"]}/{player.stats["maxhp"]}:heart:.\nYou level up {levelled_up} times!'
          )
        else:
          return await interaction.response.send_message(
            f'**{interaction.user.name}** found and killed a {enemy.emoji}{enemy.name.upper()}.\nGained {xp_result} XP and lost {initial_player_hp - player.stats["hp"]} HP. Remaining HP is {player.stats["hp"]}/{player.stats["maxhp"]}:heart:'
          )
    else:
      # Return HP to 1
      try:
        # HP First
        player.stats['hp'] = 1
        new_player = UpdatePlayerModel(stats=player.stats)
        await update_player(
          self.app, player.discord_id, new_player
        )
      except Exception as e:
        raise e

      await interaction.response.send_message(
        f':x: **{interaction.user.name}** found a {enemy.emoji}{enemy.name.upper()} and died fighting it.'
      )
      return await interaction.followup.send(
        ':regional_indicator_f:'
      )

  @hunt.error
  async def hunt_error(
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
      elif isinstance(error.original, HTTPException):
        desc = f'HTTP Error {error.original.status_code}'
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
        'Error in "hunt" (actions_cog.py)', desc
      )
    )

  # endregion

  # region Use

  @app_commands.command(
    name='use', description='Use an item.'
  )
  async def use(
    self, interaction: discord.Interaction, item: str
  ):
    # Get Player from DB
    try:
      player: PlayerModel = PlayerModel(
        **await get_player(
          self.app, discord_id=interaction.user.id
        )
      )
    except Exception as e:
      raise e

    # Check for item in inventory
    item_name = item.replace(' ', '').capitalize()

    if item_name not in player.inventory:
      return await interaction.response.send_message(
        f'You do not have {item}.'
      )

    # Get the item
    ItemClass = getattr(
      importlib.import_module('core.items'),
      item_name,
    )
    item = ItemClass()

    # Remove from inventory and actually use consumable
    await utils.remove_item(self.app, player, item_name, 1)
    if item.stat == 'hp':
      healed = await utils.heal(
        self.app, player, item.amount
      )
      return await interaction.response.send_message(
        f'You use {item.emoji}{item.name.upper()}. {healed}'
      )

  # endregion


async def setup(bot: commands.Bot):
  await bot.add_cog(ActionsCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
