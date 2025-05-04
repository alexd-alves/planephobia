class Enemy:
  def __init__(
    self,
    name: str,
    emoji: str,
    description: str,
    drops: dict[str, float],
  ) -> None:
    """Base class for all enemies.

    Args:
        name (str): Enemy's name.
        emoji (str): Enemy's emoji representation.
        description (str): Enemy's description.
        drops (dict[str, float]): Dictionary of potential loot drops and probabilities.
    """
    self.name = name
    self.emoji = emoji
    self.description = description
    self.drops = drops


class Mob(Enemy):
  """Base class for mobs. Mobs only get one turn to either die or kill the Player."""

  def __init__(
    self,
    name: str,
    emoji: str,
    description: str,
    drops: dict[str, float],
    hp: int,
    atk: int,
  ) -> None:
    super().__init__(name, emoji, description, drops)
    self.hp = hp
    self.atk = atk


class Redvelvet(Mob):
  def __init__(self) -> None:
    super().__init__(
      name='Cursed Red Velvet Cake',
      emoji=':cake:',
      description='Oops, looks like someone forgot to grease the pan!',
      drops={
        'Rumshot': 0.1,
        'Rumbottle': 0.12,
        'Sprinkles': 0.32,
        'Cakecrumbs': 0.52,
      },
      hp=8,
      atk=2,
    )


class RedvelvetCupcake(Mob):
  def __init__(self) -> None:
    super().__init__(
      name='Cursed Red Velvet Cupcake',
      emoji=':cupcake:',
      description='Just like a Cursed Red Velvet Cake... but smaller.',
      drops={
        'Rumshot': 0.05,
        'Rumbottle': 0.06,
        'Sprinkles': 0.16,
        'Cakecrumbs': 0.2,
      },
      hp=4,
      atk=1,
    )


class Bundt(Mob):
  def __init__(self) -> None:
    super().__init__(
      name='Holeless Bundt Cake',
      emoji=':pudding:',
      description='It has no hole, and it must EAT.',
      drops={
        'Rumshot': 0.15,
        'Rumbottle': 0.18,
        'Cakecrumbs': 0.25,
      },
      hp=10,
      atk=3,
    )


class CinnamonRoll(Mob):
  def __init__(self) -> None:
    super().__init__(
      name='Suspicious Cinnamon Roll',
      emoji=':waffle:',
      description='Just a normal cinnamon roll, covered in "frosting", nothing to see here.',
      drops={'Rumshot': 0.08, 'Rumbottle': 0.1},
      hp=5,
      atk=3,
    )
