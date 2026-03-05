from client.settings.settings import Settings
from client.window.window import Window
from server.server import Server
from server.world.player.player import Player
from server.world.world import World


class Client:
    def __init__(self, server: Server, world: World, player: Player):
        self.running = True

        self.server = server
        self.world = world
        self.player = player

        self.settings = Settings()
        self.window = Window(world, player)

    def main_loop(self):
        if not self.window.main_loop():
            self.running = False
