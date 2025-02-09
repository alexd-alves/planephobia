import contextlib
import datetime
import logging
import os
import threading
import time
import traceback
import typing
from typing import Generator

import aiohttp
import discord
import uvicorn
import uvicorn.server
from discord.ext import commands
from dotenv import load_dotenv

from db.db_app import app


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


# Core Bot
class PlanephobiaBot(commands.Bot):
  client: aiohttp.ClientSession
  _uptime: datetime.datetime = datetime.timezone.utc

  def __init__(
    self,
    prefix: str,
    ext_dir: str,
    *args: typing.Any,
    **kwargs: typing.Any,
  ) -> None:
    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True
    super().__init__(
      *args,
      **kwargs,
      command_prefix=commands.when_mentioned_or(prefix),
      intents=intents,
    )
    self.logger = logging.getLogger(self.__class__.__name__)
    self.ext_dir = ext_dir
    self.synced = False

  async def _load_extensions(self) -> None:
    if not os.path.isdir(self.ext_dir):
      self.logger.error(
        f'Extension directory {self.ext_dir} does not exist.'
      )
      return
    for filename in os.listdir(os.path.abspath(self.ext_dir)):
      if filename.endswith('.py') and not filename.startswith('_'):
        try:
          await self.load_extension(f'{self.ext_dir}.{filename[:-3]}')
          self.logger.info(f'Loaded extension {filename[:-3]}')
        except commands.ExtensionError:
          self.logger.error(
            f'Failed to load extension {filename[:-3]}\n{traceback.format_exc()}'
          )

  async def on_error(
    self, event_method: str, *args: typing.Any, **kwargs: typing.Any
  ) -> None:
    if (
      isinstance(args[0], discord.HTTPException)
      and args[0].status == 429
    ):
      # Rate limit encountered
      retry_after = args[0].headers.get('Retry-After')
      if retry_after:
        self.logger.warning(
          f'Rate limit encountered in {event_method}. Retrying in {retry_after}.\n{traceback.format_exc()}'
        )
        await time.sleep(int(retry_after) + 1)
      else:
        self.logger.warning(
          f'Rate limit encountered in {event_method}. No retry time given.\n{traceback.format_exc()}'
        )
        await time.sleep(1)
    else:
      # Handle other errors
      self.logger.error(
        f'An error occurred in {event_method}.\n{traceback.format_exc()}'
      )

  async def on_ready(self) -> None:
    self.logger.info(f'Logged in as {self.user} ({self.user.id})')

  async def setup_hook(self) -> None:
    self.client = aiohttp.ClientSession()

    await self._load_extensions()
    if not self.synced:
      await self.tree.sync()
      self.logger.info('Synced command tree')

  async def close(self) -> None:
    await super().close()
    await self.client.close()

  def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
    load_dotenv()
    try:
      super().run(str(os.getenv('DISCORD_TOKEN')), *args, **kwargs)
    except (discord.LoginFailure, KeyboardInterrupt):
      self.logger.info('Exiting...')
      exit()

  @property
  def user(self) -> discord.ClientUser:
    assert super().user, 'Bot is not ready yet'
    return typing.cast(discord.ClientUser, super().user)

  @property
  def uptime(self) -> datetime.timedelta:
    return datetime.timezone.utc - self._uptime


def main() -> None:
  # Set up uvicorn for db
  config = uvicorn.Config(app=app, host='localhost', port=5000)
  server = Server(config=config)
  with server.run_in_thread():
    address, port = server.config.bind_socket().getsockname()
    print(f'HTTP server is running on http://{address}.{port}')

    logging.basicConfig(
      level=logging.INFO,
      format='[%(asctime)s] %(levelname)s: %(message)s',
    )
    bot = PlanephobiaBot(prefix='!', ext_dir='cogs')

    bot.run()


if __name__ == '__main__':
  main()
else:
  print('Not Main')
