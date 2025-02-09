import discord
from pydantic import BaseModel, Field


class Player(BaseModel):
  id: discord.Member = Field(alias='_id')
  name: discord.Member.describe
