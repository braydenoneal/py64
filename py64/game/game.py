from py64.game.player.player import Player


class Game:
    def __init__(self):
        self.player = Player()

    def main_loop(self):
        self.player.position += self.player.get_direction()
