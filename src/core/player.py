from datetime import datetime, timezone

from fastapi import Request

from db.models.playerModels import Player
from db.routes import updatePlayer

# region Cooldowns


async def start_cooldown(
  req: Request, player: Player, cmd: str
) -> None:
  setattr(
    player.cooldowns, cmd, datetime.now(tz=timezone.utc).timestamp()
  )
  try:
    await updatePlayer(req, id=player.id, player=player)
  except Exception as e:
    return e


async def remove_cooldown(
  req: Request, player: Player, cmd: str
) -> None:
  setattr(player, cmd, None)
  try:
    await updatePlayer(req, id=player.id, player=player)
  except Exception as e:
    return e


async def batch_update_cooldowns(
  req: Request, player: Player
) -> None:
  try:
    await updatePlayer(req, id=player.id, player=player)
  except Exception as e:
    return e


# endregion

# region XP/Levels


# Formula for required xp for each level
def calc_req_xp(level: int) -> int:
  return (level**2) * 50


def level_up(player: Player) -> list[Player, int]:
  newplayer = player
  count = 0
  # Loop until xp has been used
  while newplayer.stats.currentxp >= newplayer.stats.requiredxp:
    newplayer.stats.currentxp -= newplayer.stats.requiredxp
    newplayer.stats.level += 1
    newplayer.stats.requiredxp = calc_req_xp(newplayer.stats.level)
    count += 1
  return [newplayer, count]


async def update_xp(req: Request, player: Player, amount: int) -> int:
  player.stats.currentxp += amount
  if player.stats.currentxp >= player.stats.requiredxp:
    leveldata = level_up(player)
    try:
      await updatePlayer(req, id=leveldata[0].id, player=leveldata[0])
      return leveldata[1]
    except Exception as e:
      return e
  else:
    # No need to level up
    try:
      await updatePlayer(req, id=player.id, player=player)
      return None
    except Exception as e:
      return e


# endregion


async def update_favor(
  req: Request, player: Player, amount: int
) -> None:
  player.favor += amount
  try:
    await updatePlayer(req, id=player.id, player=player)
  except Exception as e:
    return e
