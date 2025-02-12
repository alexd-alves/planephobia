from db.routes import updatePlayer


def level_up(player):
  newplayer = player
  while newplayer.stats.currentxp >= newplayer.stats.requiredxp:
    newplayer.stats.currentxp -= newplayer.stats.requiredxp
    newplayer.stats.level += 1
    newplayer.stats.requiredxp = (player.stats.level**2) * 50
  return newplayer


async def update_favor(req, player, amount):
  player.favor += amount
  try:
    await updatePlayer(req, id=player.id, player=player)
  except Exception as e:
    return e


async def update_xp(req, player, amount):
  player.stats.currentxp += amount
  if player.stats.currentxp >= player.stats.requiredxp:
    newplayer = level_up(player)
    try:
      await updatePlayer(req, id=newplayer.id, player=newplayer)
      return True
    except Exception as e:
      return e
  else:
    try:
      await updatePlayer(req, id=player.id, player=player)
      return False
    except Exception as e:
      return e
