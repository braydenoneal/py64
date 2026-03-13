import math

import pygame

from server.world.player.player import Player


class Input:
    def __init__(self, width: int, height: int, player: Player):
        self.width = width
        self.height = height
        self.player = player
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

        if keys[pygame.K_SPACE]:
            self.player.jump()

        pygame.event.set_grab(True)

        if pygame.mouse.get_pos() != (self.width // 2, self.height // 2):
            self.set_view_angle()
            pygame.mouse.set_pos((self.width // 2, self.height // 2))

        return True
