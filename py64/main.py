from py64.game.game import Game
from py64.window.window import Window


def main():
    game = Game()
    window = Window(game)

    while window.input.main_loop():
        game.main_loop()
        window.render.main_loop()


if __name__ == '__main__':
    main()
