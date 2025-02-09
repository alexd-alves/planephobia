import discord
from discord import app_commands
from discord.ext import commands


class SuperCog(commands.Cog):
  sub = app_commands.Group(
    name='foo',
    description='A command group Cog.',
  )

  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

  @sub.command()
  async def bar(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
      'This is a foo Cog command.'
    )

  @sub.command(name='baz')
  async def baz(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
      'This is another foo Cog command.'
    )


async def setup(bot: commands.Bot):
  await bot.add_cog(SuperCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
