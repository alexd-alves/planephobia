import contextlib
import os
import threading
import time
from typing import Generator, Optional

import discord
import uvicorn
import uvicorn.server
from discord import app_commands
from dotenv import load_dotenv

from db.db_app import app
from items import all_armor, all_consumables

# item = Consumable(all_armor[all_armor.index('rumshot')])
# print(item.name)


# Context manager to ensure db server starts and stops correctly
class Server(uvicorn.Server):
  @contextlib.contextmanager
  def run_in_thread(self) -> Generator:
    thread = threading.Thread(target=self.run)
    thread.start()
    try:
      while not self.started:
        time.sleep(0.001)
        yield
    finally:
      self.should_exit = True
      thread.join()


def main() -> int:
  # Set up uvicorn for db
  config = uvicorn.Config(app=app, host='localhost', port=5000)
  server = Server(config=config)
  with server.run_in_thread():
    address, port = server.config.bind_socket().getsockname()
    print(f'HTTP server is running on http://{address}.{port}')

    # Get environment variables
    load_dotenv()
    # DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    # TODO: Not needed in prod
    GUILD_ID = os.getenv('GUILD_ID')

    # Define intents
    intents = discord.Intents.default()
    intents.message_content = True

    # Define client
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    # Sync slash commands
    @client.event
    async def on_ready():
      await tree.sync(guild=discord.Object(id=GUILD_ID))
      print(f'Logged in as {client.user}')

    # Deal with rate limits
    @client.event
    async def on_error(event, *args, **kwargs):
      if (
        isinstance(args[0], discord.HTTPException)
        and args[0].status == 429
      ):
        # Rate limit encountered
        print('Rate limit encountered.')
        retry_after = args[0].headers.get('Retry-After')
        if retry_after:
          await time.sleep(int(retry_after) + 1)
        else:
          await time.sleep(1)
      else:
        # Handle other errors
        print(f'An error occurred: {args[0]}')

    # TODO: Remove command guild in prod
    # to allow slash commands in all guild

    # Greet
    @tree.command(
      name='greet',
      description='Greet tagged user - Test command',
      guild=discord.Object(id=GUILD_ID),
    )
    async def greet(
      interaction: discord.Interaction, user: discord.Member
    ):
      await interaction.response.send_message(
        f'Hello, {user.mention}!'
      )

    # A list of item types for testing
    @tree.command(
      name='items',
      description='Lists available items - Test command',
      guild=discord.Object(id=GUILD_ID),
    )
    @app_commands.choices(
      type=[
        app_commands.Choice(name='consumables', value='consumables'),
        app_commands.Choice(name='armour', value='armour'),
      ]
    )
    async def items(
      interaction: discord.Interaction,
      type: Optional[app_commands.Choice[str]],
    ):
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
      elif type.value == 'consumables':
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
      elif type.value == 'armour':
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
      await interaction.response.send_message(embed=items_embed)

    # Help
    @tree.command(
      name='help',
      description='A list of basic commands.',
      guild=discord.Object(id=GUILD_ID),
    )
    async def help(interaction: discord.Interaction):
      help_embed = discord.Embed(
        title='Planephobia Commands', type='rich'
      )
      help_embed.add_field(
        name='Basic Commands',
        value='`/items`: Shows all available items.\n * Arguments:\n  - `type`: Optional',
      )
      await interaction.response.send_message(embed=help_embed)

    # Run the bot
    client.run(DISCORD_TOKEN)


if __name__ == '__main__':
  main()
else:
  print('Not Main')
