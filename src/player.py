import os

import discord
from dotenv import load_dotenv

# Get environment variables
load_dotenv()
GUILD_ID = os.getenv('GUILD_ID')


class PlayerCommands(discord.app_commands.Group):
  def __init__(
    self,
    name: str,
    description: str,
    guild: str,
    tree: discord.app_commands.CommandTree,
  ):
    super().__init__(name=name, description=description)
    self.tree = tree

    @tree.command(
      name='start',
      description='Registers the Player.',
      guild=discord.Object(id=guild),
    )
    async def start(interaction: discord.Interaction):
      await interaction.response.send_message(
        'Player Commands Cog Test.'
      )


async def setup(tree: discord.app_commands.CommandTree, guild: str):
  tree.add_command(
    PlayerCommands(
      name='player',
      description='Allows Player to manage Character.',
      guild=guild,
      tree=tree,
    ),
    guild=discord.Object(id=guild),
  )
