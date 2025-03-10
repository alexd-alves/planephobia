class Item:
  # Base class for all items
  def __init__(
    self,
    name: str,
    emoji: str,
    description: str,
    value: int,
  ):
    self.name = name
    self.emoji = emoji
    self.description = description
    self.value = value


# Consumables can be consumed and change a stat
class Consumable(Item):
  def __init__(
    self,
    name: str,
    emoji: str,
    description: str,
    value: int,
    stat: str,
    amount: int,
  ):
    super().__init__(name, emoji, description, value)
    self.stat = stat
    self.amount = amount


# Consumables
class Rumshot(Consumable):
  def __init__(self):
    super().__init__(
      name='Rum Shot',
      emoji=':tumbler_glass:',
      description="A small measure of Captain Morgan Orginal Spiced Gold, GhostKai's drink of choice.",
      value=10,
      stat='hp',
      amount=5,
    )


class Rumbottle(Consumable):
  def __init__(self):
    super().__init__(
      name='Rum Bottle',
      emoji=':tumbler_glass:',
      description='A whole bottle of Captain Morgan Original Spiced Gold.',
      value=50,
      stat='hp',
      amount=10,
    )


class Cakecrumbs(Consumable):
  def __init__(self):
    super().__init__(
      name='Cake Crumbs',
      emoji=':cookie:',
      description='Some cake leftovers, not sure how fresh.',
      value=5,
      stat='hp',
      amount=3,
    )


class Sprinkles(Consumable):
  def __init__(self):
    super().__init__(
      name='Sprinkles',
      emoji=':cupcake:',
      description='A few cake sprinkles. But they are rainbow sprinkles, the objectively superior choice.',
      value=2,
      stat='hp',
      amount=1,
    )


# Armor can be worn to increase DEF and can grant other bonuses
class Armor(Item):
  def __init__(
    self,
    name: str,
    emoji: str,
    description: str,
    value: int,
    type: str,
    amount: int,
    bonuses: dict,
  ):
    super().__init__(name, emoji, description, value)
    self.type = type
    self.amount = amount
    self.bonuses = bonuses


# Armor
class Catears(Armor):
  def __init__(self):
    super().__init__(
      name='Cat Ears',
      emoji='',
      description='A headband with two pink cat ears, a type of religious headress.',
      value=25,
      type='helmet',
      amount=1,
      bonuses={'Favor': 100, 'ATK': 5},
    )


class Headset(Armor):
  def __init__(self):
    super().__init__(
      name='Steelseries Headset',
      emoji='',
      description='A new set of white Steelseries Arctis Nova headphones.',
      value=50,
      type='helmet',
      amount=5,
      bonuses={'Favor': 20, 'PER': 3},
    )


all_consumables = [Rumshot(), Rumbottle()]
all_armor = [Catears(), Headset()]
