from db.models.playerModels import Cooldowns, Stats

# Cooldowns
defaultCooldowns = Cooldowns(worship=None, duel=None, hunt=None)

# Test A
defaultStatsA = Stats(
  level=1,
  currentxp=0,
  requiredxp=100,
  maxhp=15,
  hp=15,
  maxsan=5,
  san=5,
  atk=2,
  dfs=1,
  rst=1,
  per=2,
  sth=2,
)

# Test B
defaultStatsB = Stats(
  level=1,
  currentxp=0,
  requiredxp=100,
  maxhp=10,
  maxsan=5,
  hp=10,
  atk=5,
  dfs=2,
  san=5,
  rst=2,
  per=1,
  sth=1,
)
