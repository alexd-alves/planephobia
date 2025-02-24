class Location:
  # Base Class for all locations
  def __init__(self, name, lvrange):
    self.name = (name,)
    self.lvrange = lvrange


# Planes contain clues, minibosses, and a final boss.
# They grant collectible on completion.
class Plane(Location):
  def __init__(
    self, name, lvrange, clues, minibosses, boss, collectible
  ):
    super().__init(name, lvrange)
    self.clues = clues
    self.minibosses = minibosses
    self.boss = boss
    self.collectible = collectible
