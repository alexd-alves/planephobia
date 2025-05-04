class Location:
  """Base Class for all locations"""

  def __init__(self, name, lvrange):
    self.name = (name,)
    self.lvrange = lvrange


class Plane(Location):
  def __init__(
    self,
    name,
    lvrange,
    clues,
    minibosses,
    boss,
    collectible,
  ):
    """Planes contain clues, miniboses and a final boss, and grant a collectible on completion.

    Args:
        name (_type_): Name of the plane.
        lvrange (_type_): Level range of the location.
        clues (_type_): Clues present in the plane.
        minibosses (_type_): Minibosses present in the plane.
        boss (_type_): Plane's final boss.
        collectible (_type_): Collectible obtained by completing location.
    """
    super().__init(name, lvrange)
    self.clues = clues
    self.minibosses = minibosses
    self.boss = boss
    self.collectible = collectible
