from client.client import Client
from server.server import Server


def main():
    server = Server()
    world = server.world
    player = world.player
    client = Client(server, world, player)

    while server.running and client.running:
        server.main_loop()
        client.main_loop()


if __name__ == '__main__':
    main()
