class Enemy:
  # Base class for all enemies
  def __init__(self, name: str, description: str) -> None:
    self.name = name
    self.description = description


class Mob(Enemy):
  # Mobs only get one turn to either die or kill the Player
  def __init__(
    self, name: str, description: str, hp: int, atk: int
  ) -> None:
    super().__init__(name, description)
    self.hp = hp
    self.atk = atk


class Redvelvet(Mob):
  def __init__(self) -> None:
    super().__init__(
      name='Cursed Red Velvet Cake',
      description='Oops, looks like someone forgot the non-stick paper!',
      hp=8,
      atk=1,
    )
