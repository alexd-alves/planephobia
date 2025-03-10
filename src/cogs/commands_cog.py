import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import utility.embeds as embeds
from core.items import all_armor, all_consumables
from db.routes import delete_player, list_players


class CommandsCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.app = bot.app
    self.bot = bot

  # A list of item types for testing
  @app_commands.command(
    name='items',
    description='Test Command: List of all Items.',
  )
  @app_commands.choices(
    type=[
      app_commands.Choice(
        name='consumables', value='consumables'
      ),
      app_commands.Choice(name='armor', value='armor'),
    ]
  )
  async def items(
    self,
    interaction: discord.Interaction,
    type: app_commands.Choice[str] | None,
  ) -> None:
    if not type:
      consumables_list = []

      for item in all_consumables:
        consumables_list.append(
          '**' + item.name + '** - ' + item.description
        )
        consumables_list.append(
          '* Value: ' + str(item.value) + ' tokens'
        )
        consumables_list.append(
          '* +' + str(item.amount) + ' ' + item.stat
        )
      consumables_list = '\n'.join(consumables_list)

      armor_list = []

      for item in all_armor:
        bonuses = ', '.join(
          '{}: +{}'.format(*i) for i in item.bonuses.items()
        )

        armor_list.append(
          '**'
          + item.name
          + '** - '
          + item.type.capitalize()
          + '. '
          + item.description
        )
        armor_list.append('* DEF: +' + str(item.amount))
        armor_list.append('* Also grants: ' + bonuses)
        armor_list.append(
          '* Value: ' + str(item.value) + ' tokens'
        )
      armor_list = '\n'.join(armor_list)

      items_embed = discord.Embed(
        title='Available Items',
        description='The items available are:',
        type='rich',
      )

      items_embed.add_field(
        name='Consumables',
        value=consumables_list,
        inline=True,
      )
      items_embed.add_field(
        name='Armor', value=armor_list, inline=True
      )

    elif type.value == 'consumables':
      item_list = []

      for item in all_consumables:
        item_list.append(
          '**' + item.name + '** - ' + item.description
        )
        item_list.append(
          '* Value: ' + str(item.value) + ' tokens'
        )
        item_list.append(
          '* +' + str(item.amount) + ' ' + item.stat
        )
      item_list = '\n'.join(item_list)

      items_embed = discord.Embed(
        title='Available Items',
        description='The items available are:',
        type='rich',
      )

      items_embed.add_field(
        name='Consumables', value=item_list, inline=False
      )
    elif type.value == 'armor':
      item_list = []

      for item in all_armor:
        bonuses = ', '.join(
          '{}: +{}'.format(*i) for i in item.bonuses.items()
        )

        item_list.append(
          '**'
          + item.name
          + '** - '
          + item.type.capitalize()
          + '. '
          + item.description
        )
        item_list.append('* DEF: +' + str(item.amount))
        item_list.append('* Also grants: ' + bonuses)
        item_list.append(
          '* Value: ' + str(item.value) + ' tokens'
        )
      item_list = '\n'.join(item_list)

      items_embed = discord.Embed(
        title='Available Items',
        description='The items available are:',
        type='rich',
      )

      items_embed.add_field(name='Armour', value=item_list)

    await interaction.response.send_message(
      embed=items_embed
    )

  # Help
  @app_commands.command(
    name='help',
    description='How to play.',
  )
  async def help(self, interaction: discord.Interaction):
    await interaction.response.send_message(
      embed=embeds.HelpEmbed()
    )

  # List All Players
  @app_commands.command(
    name='players', description='List all Players.'
  )
  async def list(self, interaction: discord.Interaction):
    await interaction.response.send_message(
      await list_players(self.app)
    )

  # Development utilities
  # Extension Reload
  @app_commands.command(
    name='reload',
    description='Dev Command: Reload an extension.',
  )
  async def reload(
    self, interaction: discord.Integration, extension: str
  ):
    await self.bot.reload_extension(f'{extension}')
    await interaction.response.send_message(
      f'Reloaded {extension}.'
    )

  # @reload.autocomplete('extension')
  # async def extension_autocomplete(
  #   self, interaction: discord.Interaction, current: str
  # ) -> list[app_commands.Choice[str]]:
  #   extensions = list(self.bot.extensions.keys())
  #   options: list[app_commands.Choice[str]] = []
  #   for ext in extensions:
  #     if ext.startswith(current):
  #       options.append(
  #         app_commands.Choice(name=ext, value=ext)
  #       )
  #   return options[:25]

  # Command Sync
  @app_commands.command(
    name='sync', description='Re-sync all commands.'
  )
  @commands.is_owner()
  async def sync(self, interaction: discord.Interaction):
    try:
      synced = await self.bot.tree.sync()
      await interaction.response.defer()
      await asyncio.sleep(3)
      await interaction.followup.send(
        f'Synced {len(synced)} commands globally.'
      )
    except Exception as e:
      raise e

  # Delete Player Record
  @app_commands.command(
    name='yeet', description='Delete Player from DB.'
  )
  async def yeet(
    self,
    interaction: discord.Interaction,
    user: discord.Member,
  ) -> None:
    try:
      await delete_player(self.app, discord_id=user.id)
      await interaction.response.send_message(
        f'{user.id} has been deleted.'
      )
    except Exception as e:
      raise e


async def setup(bot: commands.Bot):
  await bot.add_cog(CommandsCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
