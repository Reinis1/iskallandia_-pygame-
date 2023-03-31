from data.scripts.classes.map.generator import Generator


class GenManager:
    def __init__(self, terrain):
        self.gens = []
        for gen in terrain.gens:
            self.gens.append(Generator(gen[0], gen[1]))

    def update(self, terrain, player, effect):
        for gen in self.gens:
            gen.update(terrain, player, effect)
