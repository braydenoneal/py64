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
                elif event.key == pygame.K_w:
                    self.player.move_forward()
                elif event.key == pygame.K_s:
                    self.player.move_backward()
                elif event.key == pygame.K_a:
                    self.player.move_left()
                elif event.key == pygame.K_d:
                    self.player.move_right()
                elif event.key == pygame.K_SPACE:
                    self.player.move_up()
                elif event.key == pygame.K_LSHIFT:
                    self.player.move_down()

        # keys = pygame.key.get_pressed()
        #
        # if keys[pygame.K_w]:
        #     self.player.move_forward()
        # if keys[pygame.K_s]:
        #     self.player.move_backward()
        # if keys[pygame.K_a]:
        #     self.player.move_left()
        # if keys[pygame.K_d]:
        #     self.player.move_right()
        # if keys[pygame.K_SPACE]:
        #     self.player.move_up()
        # if keys[pygame.K_LSHIFT]:
        #     self.player.move_down()

        pygame.event.set_grab(True)

        if pygame.mouse.get_pos() != (self.width // 2, self.height // 2):
            self.set_view_angle()
            pygame.mouse.set_pos((self.width // 2, self.height // 2))

        return True
