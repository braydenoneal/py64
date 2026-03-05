from server.world.world import World


class Server:
    def __init__(self):
        self.running = True
        self.world = World()

    def main_loop(self):
        self.world.main_loop()
