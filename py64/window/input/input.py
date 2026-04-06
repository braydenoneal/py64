import math

import pygame

from py64.game.game import Game


class Input:
    def __init__(self, game: Game, width: int, height: int):
        self.game = game
        self.player = game.player
        self.width = width
        self.height = height
        pygame.mouse.set_pos((self.width // 2, self.height // 2))

    def set_view_angle(self):
        x, y = pygame.mouse.get_pos()
        dx = x - self.width // 2
        dy = y - self.height // 2
        self.player.x_angle -= dy / 500
        self.player.x_angle = min(max(self.player.x_angle, -math.pi / 2), math.pi / 2)
        self.player.y_angle -= dx / 500
        self.player.y_angle %= 2 * math.pi

    def main_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False

        keys = pygame.key.get_pressed()

        self.player.movement['forward'] = keys[pygame.K_w]
        self.player.movement['backward'] = keys[pygame.K_s]
        self.player.movement['left'] = keys[pygame.K_a]
        self.player.movement['right'] = keys[pygame.K_d]
        self.player.movement['up'] = keys[pygame.K_SPACE]
        self.player.movement['down'] = keys[pygame.K_LSHIFT]

        pygame.event.set_grab(True)

        if pygame.mouse.get_pos() != (self.width // 2, self.height // 2):
            self.set_view_angle()
            pygame.mouse.set_pos((self.width // 2, self.height // 2))

        return True
