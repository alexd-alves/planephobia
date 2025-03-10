from datetime import datetime, timezone

from db.models.playerModel import PlayerModel
from db.models.updatePlayerModel import UpdatePlayerModel
from db.routes import update_player

# region Cooldowns


async def start_cooldown(
  app, player: PlayerModel, cmd: str
) -> None:
  cooldowns = player.cooldowns
  cooldowns[cmd] = datetime.now(tz=timezone.utc).timestamp()

  new_player = UpdatePlayerModel(cooldowns=cooldowns)
  try:
    await update_player(
      app, discord_id=player.discord_id, player=new_player
    )
  except Exception as e:
    return e


async def remove_cooldown(
  app, player: PlayerModel, cmd: str
) -> None:
  cooldowns = player.cooldowns
  cooldowns[cmd] = None

  new_player = UpdatePlayerModel(cooldowns=cooldowns)
  try:
    await update_player(
      app, discord_id=player.discord_id, player=new_player
    )
  except Exception as e:
    return e


# endregion

# region XP/Levels


def level_up(
  player: PlayerModel,
) -> list[UpdatePlayerModel, int]:
  count = 0
  # Loop until xp has been used
  while (
    player.stats['currentxp'] >= player.stats['requiredxp']
  ):
    player.stats['currentxp'] -= player.stats['requiredxp']
    player.stats['level'] += 1
    player.stats['requiredxp'] = (
      player.calculate_next_lv_xp()
    )
    count += 1

  new_player = UpdatePlayerModel(stats=player.stats)

  return [new_player, count]


async def update_xp(
  app, player: PlayerModel, amount: int
) -> int:
  player.stats['currentxp'] += amount
  if player.stats['currentxp'] < 0:
    player.stats['currentxp'] = 0
  if (
    player.stats['currentxp'] >= player.stats['requiredxp']
  ):
    leveldata = level_up(player)

    try:
      await update_player(
        app,
        discord_id=player.discord_id,
        player=leveldata[0],
      )
      return leveldata[1]
    except Exception as e:
      return e
  else:
    # No need to level up
    new_player = UpdatePlayerModel(stats=player.stats)

    try:
      await update_player(
        app, discord_id=player.discord_id, player=new_player
      )
      return None
    except Exception as e:
      return e


# endregion

# region Favor/Tokens


async def update_favor(
  app, player: PlayerModel, amount: int
) -> None:
  new_player = UpdatePlayerModel(
    favor=(player.favor + amount)
  )
  try:
    await update_player(
      app, discord_id=player.discord_id, player=new_player
    )
  except Exception as e:
    return e


# endregion

# region Inventory


async def add_item(
  app, player: PlayerModel, item: str, amount: int
) -> None:
  inventory = player.inventory

  if inventory is None:
    # Create the inventory dict with the item given
    inventory = {item: amount}
  else:
    # Check it item exists
    if item in inventory:
      inventory[item] += amount
    else:
      inventory[item] = amount

  new_player = UpdatePlayerModel(inventory=inventory)
  try:
    await update_player(
      app, discord_id=player.discord_id, player=new_player
    )
  except Exception as e:
    return e


async def remove_item(
  app, player: PlayerModel, item: str, amount: int
) -> None:
  inventory = player.inventory

  inventory[item] -= amount

  # Remove from inventory fully if none left
  if inventory[item] <= 0:
    del inventory[item]

  new_player = UpdatePlayerModel(inventory=inventory)
  try:
    await update_player(
      app, discord_id=player.discord_id, player=new_player
    )
  except Exception as e:
    return e


# endregion


async def heal(
  app, player: PlayerModel, amount: int
) -> str:
  player.stats['hp'] = player.stats['hp'] + amount
  if player.stats['hp'] > player.stats['maxhp']:
    player.stats['hp'] = player.stats['maxhp']
    new_player = UpdatePlayerModel(stats=player.stats)
    try:
      await update_player(
        app, discord_id=player.discord_id, player=new_player
      )
      return 'Your health is fully restored.'
    except Exception as e:
      return e

  else:
    new_player = UpdatePlayerModel(stats=player.stats)
    try:
      await update_player(
        app, discord_id=player.discord_id, player=new_player
      )

      return f'You have healed {amount} HP. Your HP is now {player.stats["hp"]}/{player.stats["maxhp"]}.'
    except Exception as e:
      return e
