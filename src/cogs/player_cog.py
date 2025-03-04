import random
from datetime import datetime, timezone
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from pydantic import ValidationError

import core.enemies as enemies
import core.player as player
import core.titles as titles
import utility.buttons as buttons
import utility.embeds as embeds
import utility.playerClasses as playerClasses
from db.models.playerModels import Player
from db.routes import addPlayer, getPlayerByDiscordId, updatePlayer

# region Settings
cooldownCmds = ['worship', 'duel', 'hunt']
cooldowns = {'worship': 5, 'duel': 10, 'hunt': 1}

worship_dance_outcomes = {
  'You fail miserably, do you even know where left and right are? You have upset GhostKai.\nYou get -5 Favour.': -5,
  'You look ridiculous, but at least you managed to stay on your feet. However, GhostKai has standards.\n You get -1 Favour.': -1,
  'Mediocre, but it will have to do.\nYou get +1 Favour!': 1,
  'Your dance is adequate, GhostKai is pleased.\nYou get +3 Favour!': 3,
  'The light of our Lord GhostKai shines upon you! Your dance has greatly pleased Him.\nYou get +5 Favour!': 5,
}
worship_dance_weights = [5, 10, 40, 35, 10]
# endregion


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
        addedPlayer = await addPlayer(req, player=newPlayer)
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
        addedPlayer = await addPlayer(req, player=newPlayer)
        await interaction.followup.send(
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

  # Cooldowns
  @app_commands.command(
    name='cooldowns', description='Display full player stats.'
  )
  async def cooldowns(self, interaction: discord.Interaction) -> None:
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
        embed=embeds.NotRegisteredEmbed()
      )

    # Get cooldowns
    playerCooldowns = playerObject.cooldowns
    # Filter out special methods and create dict
    remainingDeltas: dict[str, str] = {}
    # Get all time diffs and update to None if exceeded
    for attr in cooldownCmds:
      timestamp = getattr(playerCooldowns, attr)
      if timestamp:
        timeSince = datetime.now(timezone.utc).timestamp() - timestamp
        timeRemaining = (cooldowns.get(attr) * 60) - timeSince
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
      await player.batch_update_cooldowns(req, playerObject)
    except Exception as e:
      return await interaction.response.send_message(
        embed=embeds.ExceptionEmbed(extras=e)
      )

    # If i use at 2:10 and cooldown is 10, and i call cooldown at 2:15
    # 2:15 - 2:20 (2:10 plus cooldown) is -5 minutes
    # so when time now - time plus cooldown is negative cooldown stays???
    # if datetime.now().timestamp() - (timestamp + detatime(minutes='cooldown')) >= 0: remove timestamp
    return await interaction.response.send_message(remainingDeltas)

  # Worship
  @app_commands.command(
    name='worship', description='Worship our Lord GhostKai!'
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

    # Player Not Found
    if not playerObject:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Check cooldown
    cooldown = playerObject.cooldowns.cooldown_by_name(
      cooldowns, 'worship'
    )
    if cooldown:
      return await interaction.response.send_message(cooldown)

    if type.value == 'dance':
      dance_result = random.choices(
        list(worship_dance_outcomes.keys()), worship_dance_weights
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
        await player.start_cooldown(req, playerObject, 'worship')
      except Exception as e:
        return await interaction.response.send_message(
          embed=embeds.ExceptionEmbed(extras=e)
        )

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

  # Duel
  @app_commands.command(
    name='duel', description='Fight other players 1v1.'
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
    req = self.bot.app

    # Tagging oneself
    if interaction.user.id == target.id:
      return await interaction.response.send_message(
        'You cannot tag yourself.'
      )

    # Get both players from db
    try:
      initPlayer = await getPlayerByDiscordId(
        req, discord_id=interaction.user.id
      )
      targetPlayer = await getPlayerByDiscordId(
        req, discord_id=target.id
      )
      if (
        initPlayer is ValidationError
        or targetPlayer is ValidationError
      ):
        return await interaction.response.send_message(
          embed=embeds.ValidationErrorEmbed(
            extras=' * **`player.py/duel - getPlayerByDiscordId()`:** `initPlayer` or `targetPlayer` is of Type `ValidationError`.',
            display=True,
          )
        )
    except Exception as e:
      return await interaction.response.send_message(
        embed=embeds.ExceptionEmbed(extras=e)
      )

    # region Other Checks
    # Player Not Found
    if not initPlayer:
      return await interaction.response.send_message(
        embed=embeds.NotRegisteredEmbed()
      )

    # Target Not Found
    if not targetPlayer:
      return await interaction.response.send_message(
        "Target Player doesn't exist."
      )

    # Check cooldown for initiator
    cooldown = initPlayer.cooldowns.cooldown_by_name(
      cooldowns, 'duel'
    )
    if cooldown:
      return await interaction.response.send_message(cooldown)

    # Check cooldown for target
    cooldown = targetPlayer.cooldowns.cooldown_by_name_for_target(
      target.name, cooldowns, 'duel'
    )
    if cooldown:
      return await interaction.response.send_message(cooldown)
    # endregion

    if type.value == 'dice':
      view = buttons.DuelConsentButton(
        timeout=180, init=interaction.user.id, target=target.id
      )
      await interaction.response.send_message(
        f"{interaction.user.name} has challenged {target.name} to a dice duel!\nDo you accept **{interaction.user.name}**'s challenge, {target.mention}?",
        view=view,
      )
      view.response = await interaction.original_response()
      await view.wait()
      if view.value:
        # Update Cooldowns
        try:
          await player.start_cooldown(req, initPlayer, 'duel')
          await player.start_cooldown(req, targetPlayer, 'duel')
        except Exception as e:
          return await interaction.response.send_message(
            embed=embeds.ExceptionEmbed(extras=e)
          )

        # Actual dice rolling
        initPlayerRoll = random.randint(1, 20)
        targetPlayerRoll = random.randint(1, 20)

        # If tie
        if initPlayerRoll == targetPlayerRoll:
          # Calculate XP using gaussian distribution
          init_mu = initPlayer.stats.level * 25
          init_sigma = initPlayer.stats.level * 5
          init_xp = int(random.gauss(init_mu, init_sigma))

          target_mu = targetPlayer.stats.level * 25
          target_sigma = targetPlayer.stats.level * 5
          target_xp = int(random.gauss(target_mu, target_sigma))

          # Update XPs
          try:
            # Initiator
            init_levelled_up = await player.update_xp(
              req=req,
              player=initPlayer,
              amount=init_xp,
            )
            # Target
            target_levelled_up = await player.update_xp(
              req=req,
              player=targetPlayer,
              amount=target_xp,
            )
          except Exception as e:
            return await interaction.response.send_message(
              embed=embeds.ExceptionEmbed(extras=e)
            )

          followup = await interaction.followup.send(
            f"{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\nIt's a tie!"
          )
          if init_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP. You level up {init_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP.'
            )

          if target_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.name} gains {init_xp} XP. You level up {init_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.name} gains {init_xp} XP.'
            )
        # Initiatior wins
        elif initPlayerRoll > targetPlayerRoll:
          # Calculate XP using gaussian distribution
          init_mu = initPlayer.stats.level * 50
          init_sigma = initPlayer.stats.level * 5
          init_xp = int(random.gauss(init_mu, init_sigma))

          # Update XP
          try:
            init_levelled_up = await player.update_xp(
              req=req,
              player=initPlayer,
              amount=init_xp,
            )
          except Exception as e:
            return await interaction.response.send_message(
              embed=embeds.ExceptionEmbed(extras=e)
            )

          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\n**{interaction.user.name}** wins!'
          )
          if init_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP. {interaction.user.name} levels up {init_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP.'
            )
        # Target wins
        elif targetPlayerRoll > initPlayerRoll:
          # Calculate XP using gaussian distribution
          target_mu = targetPlayer.stats.level * 50
          target_sigma = targetPlayer.stats.level * 5
          target_xp = int(random.gauss(target_mu, target_sigma))

          # Update XPs
          try:
            target_levelled_up = await player.update_xp(
              req=req,
              player=targetPlayer,
              amount=target_xp,
            )
          except Exception as e:
            return await interaction.response.send_message(
              embed=embeds.ExceptionEmbed(extras=e)
            )

          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\n**{target.name}** wins!'
          )
          if target_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{target.name} gains {target_xp} XP. {target.name} levels up {target_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{target.name} gains {target_xp} XP.'
            )

    elif type.value == 'dice hardcore':
      view = buttons.DuelConsentButton(
        timeout=10, init=interaction.user.id, target=target.id
      )
      await interaction.response.send_message(
        f"{interaction.user.name} has challenged {target.name} to a hardcore dice duel!\nDo you accept **{interaction.user.name}**'s challenge, {target.mention}?",
        view=view,
      )
      view.response = await interaction.original_response()
      await view.wait()
      if view.value:
        # Update Cooldowns
        try:
          await player.start_cooldown(req, initPlayer, 'duel')
          await player.start_cooldown(req, targetPlayer, 'duel')
        except Exception as e:
          return await interaction.response.send_message(
            embed=embeds.ExceptionEmbed(extras=e)
          )

        # Actual dice rolling
        initPlayerRoll = random.randint(1, 20)
        targetPlayerRoll = random.randint(1, 20)

        # If tie
        if initPlayerRoll == targetPlayerRoll:
          # No XP win or loss
          followup = await interaction.followup.send(
            f"{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\nIt's a tie! No one gets anything."
          )
        # Initiatior wins
        elif initPlayerRoll > targetPlayerRoll:
          # Calculate XP win for initiator using gaussian distribution
          init_mu = initPlayer.stats.level * 50
          init_sigma = initPlayer.stats.level * 5
          init_xp = int(random.gauss(init_mu, init_sigma))

          # Calculate XP loss for target
          target_mu = initPlayer.stats.level * 50
          target_sigma = initPlayer.stats.level * 5
          target_xp = int(random.gauss(init_mu, init_sigma)) * -1

          # Update XP
          try:
            init_levelled_up = await player.update_xp(
              req=req,
              player=initPlayer,
              amount=init_xp,
            )
            target_levelled_up = await player.update_xp(
              req=req,
              player=targetPlayer,
              amount=target_xp,
            )
          except Exception as e:
            return await interaction.response.send_message(
              embed=embeds.ExceptionEmbed(extras=e)
            )

          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\n**{interaction.user.name}** wins!'
          )
          if init_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP. {interaction.user.name} levels up {init_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{interaction.user.name} gains {init_xp} XP.'
            )
          followup = await followup.edit(
            content=f'{followup.content}\n{target.name} loses {target_xp * -1} XP.'
          )
        # Target wins
        elif targetPlayerRoll > initPlayerRoll:
          # Calculate target XP win using gaussian distribution
          target_mu = targetPlayer.stats.level * 50
          target_sigma = targetPlayer.stats.level * 5
          target_xp = int(random.gauss(target_mu, target_sigma))

          # Calculate initiator's loss
          init_mu = initPlayer.stats.level * 50
          init_sigma = initPlayer.stats.level * 5
          init_xp = int(random.gauss(target_mu, target_sigma)) * -1

          # Update XPs
          try:
            target_levelled_up = await player.update_xp(
              req=req,
              player=targetPlayer,
              amount=target_xp,
            )
            init_levelled_up = await player.update_xp(
              req=req,
              player=initPlayer,
              amount=init_xp,
            )
          except Exception as e:
            return await interaction.response.send_message(
              embed=embeds.ExceptionEmbed(extras=e)
            )

          followup = await interaction.followup.send(
            f'{interaction.user.name}: {initPlayerRoll}\n{target.name}: {targetPlayerRoll}\n**{target.name}** wins!'
          )
          if target_levelled_up:
            followup = await followup.edit(
              content=f'{followup.content}\n{target.name} gains {target_xp} XP. {target.name} levels up {target_levelled_up} times!'
            )
          else:
            followup = await followup.edit(
              content=f'{followup.content}\n{target.name} gains {target_xp} XP.'
            )
          followup = await followup.edit(
            content=f'{followup.content}\n{interaction.user.name} loses {init_xp * -1} XP.'
          )

  # Hunt?
  @app_commands.command(name='hunt', description='Hunt small mobs.')
  async def hunt(self, interaction: discord.Interaction):
    req = self.bot.app

    # Get Player from DB
    try:
      playerObject = await getPlayerByDiscordId(
        req, discord_id=interaction.user.id
      )
      if playerObject is ValidationError:
        return await interaction.response.send_message(
          embed=embeds.ValidationErrorEmbed(
            extras=' * **`player_cog.py/hunt - getPlayerByDiscordId()`:** `playerObject` is of Type `ValidationError`.',
            display=True,
          )
        )
    except Exception as e:
      return await interaction.response.send_message(
        embed=embeds.ExceptionEmbed(extras=e)
      )

    # Check Cooldown
    timestamp = getattr(playerObject.cooldowns, 'hunt')
    if timestamp:
      timeSince = datetime.now(timezone.utc).timestamp() - timestamp
      timeRemaining = (cooldowns.get('hunt') * 60) - timeSince
      if timeRemaining > 0:
        minutes, seconds = divmod(timeRemaining, 60)
        hours, minutes = divmod(minutes, 60)
        return await interaction.response.send_message(
          'You have %d:%02d:%02d of cooldown remaining'
          % (
            hours,
            minutes,
            seconds,
          )
        )

    # Update Cooldown
    try:
      await player.start_cooldown(req, playerObject, 'hunt')
    except Exception as e:
      return await interaction.response.send_message(
        embed=embeds.ExceptionEmbed(extras=e)
      )

    enemy = enemies.Redvelvet()
    initialhp = playerObject.stats.hp

    # Player takes turn first
    while playerObject.stats.hp > 0 and enemy.hp > 0:
      # Player's turn
      enemy.hp = enemy.hp - playerObject.stats.atk
      print(f'New enemy HP: {enemy.hp}')
      # Enemy's turn
      if enemy.hp > 0:
        playerObject.stats.hp = int(
          playerObject.stats.hp
          - (enemy.atk * (80 / 100 + playerObject.stats.dfs))
        )
        print(f'new hp: {playerObject.stats.hp}')

    if playerObject.stats.hp > 0:
      # Calculate XP using gaussian distribution
      xp_mu = playerObject.stats.level * 35
      xp_sigma = playerObject.stats.level * 5
      acq_xp = int(random.gauss(xp_mu, xp_sigma))

      # Update XP and HP
      try:
        # HP First
        await updatePlayer(req, playerObject.id, playerObject)
        print('Updated HP')

        # Then XP
        levelled_up = await player.update_xp(
          req=req, player=playerObject, amount=acq_xp
        )
        print('Updated XP')
      except Exception as e:
        return await interaction.response.send_message(
          embed=embeds.ExceptionEmbed(extras=e)
        )

      if levelled_up:
        return await interaction.response.send_message(
          f'**{interaction.user.name}** found and killed a {enemy.name.upper()}.\nGained {acq_xp} XP and lost {initialhp - playerObject.stats.hp} HP. Remaining HP is {playerObject.stats.hp}/{playerObject.stats.maxhp}.\nYou level up {levelled_up} times!'
        )
      else:
        return await interaction.response.send_message(
          f'**{interaction.user.name}** found and killed a {enemy.name.upper()}.\nGained {acq_xp} XP and lost {initialhp - playerObject.stats.hp} HP. Remaining HP is {playerObject.stats.hp}/{playerObject.stats.maxhp}.'
        )
    else:
      return await interaction.response.send_message(
        f'**{interaction.user.name}** found a {enemy.name.upper()} and died fighting it.'
      )


async def setup(bot: commands.Bot):
  await bot.add_cog(PlayerCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
