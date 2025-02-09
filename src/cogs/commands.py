from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from items import all_armor, all_consumables


class CommandsCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

  # Greet
  @app_commands.command(
    name='greet', description='Greet tagged user - Test command'
  )
  async def greet(
    self,
    interaction: discord.Interaction,
    user: discord.Member,
  ):
    await interaction.response.send_message(f'Hello, {user.mention}!')

  # A list of item types for testing
  @app_commands.command(
    name='items',
    description='Lists available items - Test command',
  )
  @app_commands.choices(
    itemtype=[
      app_commands.Choice(name='consumables', value='consumables'),
      app_commands.Choice(name='armour', value='armour'),
    ]
  )
  async def items(
    self,
    interaction: discord.Interaction,
    itemtype: Optional[app_commands.Choice[str]],
  ) -> None:
    if itemtype.value == 'consumables':
      item_list = []

      for item in all_consumables:
        item_list.append(
          '**' + item.name + '** - ' + item.description
        )
        item_list.append('* Value: ' + str(item.value) + ' tokens')
        item_list.append('* +' + str(item.amount) + ' ' + item.stat)
      item_list = '\n'.join(item_list)

      items_embed = discord.Embed(
        title='Available Items',
        description='The items available are:',
        type='rich',
      )

      items_embed.add_field(
        name='Consumables', value=item_list, inline=False
      )
    elif itemtype.value == 'armour':
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
        item_list.append('* Value: ' + str(item.value) + ' tokens')
      item_list = '\n'.join(item_list)

      items_embed = discord.Embed(
        title='Available Items',
        description='The items available are:',
        type='rich',
      )

      items_embed.add_field(name='Armour', value=item_list)
    else:
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
        armor_list.append('* Value: ' + str(item.value) + ' tokens')
      armor_list = '\n'.join(armor_list)

      items_embed = discord.Embed(
        title='Available Items',
        description='The items available are:',
        type='rich',
      )

      items_embed.add_field(
        name='Consumables', value=consumables_list, inline=True
      )
      items_embed.add_field(
        name='Armour', value=armor_list, inline=True
      )

    await interaction.response.send_message(embed=items_embed)

  # Help
  @app_commands.command(
    name='help',
    description='A list of basic commands.',
  )
  async def help(self, interaction: discord.Interaction):
    help_embed = discord.Embed(
      title='Planephobia Commands', type='rich'
    )
    help_embed.add_field(
      name='Basic Commands',
      value='`/items`: Shows all available items.\n * Arguments:\n  - `type`: Optional',
    )
    await interaction.response.send_message(embed=help_embed)


async def setup(bot: commands.Bot):
  await bot.add_cog(CommandsCog(bot))


async def teardown(bot: commands.Bot):
  print('Extension unloaded.')
