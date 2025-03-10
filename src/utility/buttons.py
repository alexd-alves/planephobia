import discord


class DuelConsentButton(discord.ui.View):
  def __init__(
    self, *, timeout: int = 180, init: int, target: int
  ):
    super().__init__(timeout=timeout)
    self.value = None
    self.init = init
    self.target = target

  @discord.ui.button(
    label='YES', style=discord.ButtonStyle.green
  )
  async def yes(
    self,
    interaction: discord.Interaction,
    button: discord.ui.Button,
  ):
    if interaction.user.id == self.target:
      self.value = True
      self.stop()
      return await interaction.response.edit_message(
        content='Duel accepted.', view=None
      )

  @discord.ui.button(
    label='NO', style=discord.ButtonStyle.red
  )
  async def no(
    self,
    interaction: discord.Interaction,
    button: discord.ui.Button,
  ):
    self.stop()
    return await interaction.response.edit_message(
      content='Duel cancelled.', view=None
    )

  async def interaction_check(
    self, interaction: discord.Interaction
  ):
    return (
      interaction.user.id == self.target
      or interaction.user.id == self.init
    )

  async def on_error(
    self,
    interaction: discord.Interaction,
    error: Exception,
    item,
  ):
    return await super().on_error(interaction, error, item)

  async def on_timeout(self):
    for item in self.children:
      item.disabled = True
    if self.response:
      self.response = await self.response.fetch()
      await self.response.edit(
        content=f'{self.response.content}\nDuel has timed out.',
        view=self,
      )
    return await super().on_timeout()


class PlayerClassButtons(discord.ui.View):
  def __init__(self, *, timeout: int = 180):
    super().__init__(timeout=timeout)
    self.value = None

  @discord.ui.button(
    label='Test Class A', style=discord.ButtonStyle.grey
  )
  async def test_a(
    self,
    interaction: discord.Interaction,
    button: discord.ui.Button,
  ):
    self.value = 'a'
    self.stop()
    return await interaction.response.edit_message(
      content='Test Class A chosen.', view=None
    )

  @discord.ui.button(
    label='Test Class B', style=discord.ButtonStyle.grey
  )
  async def test_b(
    self,
    interaction: discord.Interaction,
    button: discord.ui.Button,
  ):
    self.value = 'b'
    self.stop()
    return await interaction.response.edit_message(
      content='Test Class B chosen.', view=None
    )

  async def on_error(
    self,
    interaction: discord.Interaction,
    error: Exception,
    item,
  ):
    return await super().on_error(interaction, error, item)

  async def on_timeout(self):
    for item in self.children:
      item.disabled = True
    if self.response:
      self.response = await self.response.fetch()
      await self.response.edit(
        content=f'{self.response.content}\nDuel has timed out.',
        view=self,
      )
    return await super().on_timeout()
