import random
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

import core.titles as titles


class Stats(BaseModel):
  level: int
  currentxp: int
  requiredxp: int
  maxhp: int
  hp: int
  maxsan: int
  san: int
  atk: int
  dfs: int
  rst: int
  per: int
  sth: int


class Cooldowns(BaseModel):
  worship: float | None
  duel: float | None
  hunt: float | None

  def cooldown_by_name(
    self,
    cooldowns: dict,
    command: str,
    target: Optional[str] = None,
  ) -> str | None:
    timestamp = getattr(self, command)
    if timestamp:
      timeSince = (
        datetime.now(timezone.utc).timestamp() - timestamp
      )
      timeRemaining = (
        cooldowns.get(command) * 60
      ) - timeSince
      if timeRemaining > 0:
        minutes, seconds = divmod(timeRemaining, 60)
        hours, minutes = divmod(minutes, 60)
        if target:
          return f'Try again in {
            "%d:%02d:%02d"
            % (
              hours,
              minutes,
              seconds,
            )
          }'
        elif target is None:
          return f'**{target}** has {
            "%d:%02d:%02d"
            % (
              hours,
              minutes,
              seconds,
            )
          } of cooldown remaining'


class Player(BaseModel):
  id: Optional[str] = Field(
    default_factory=str, alias='_id'
  )
  discord_id: int
  title: str = Field(default=titles.PlayerTitles._1)
  playerClass: str
  stats: Stats
  tokens: int
  favor: int
  inventory: dict[str, int] | None = None
  cooldowns: Cooldowns
  registered_at: datetime

  def calculate_xp_gauss(
    self, m_multiplier: int, s_multiplier: int
  ) -> int:
    xp_mu = self.stats.level * m_multiplier
    xp_sigma = self.stats.level * s_multiplier
    return int(random.gauss(xp_mu, xp_sigma))
