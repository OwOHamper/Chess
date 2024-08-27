import pygame
# from src.constants import SQUARE_SIZE, rows, columns, background, tile, highlight_color, height, width
from src.constants import *

class Board():
    def __init__(self, screen):
        global board_scale
        self.screen = screen
        self.theme = "bases"
        self.board = pygame.image.load(f"./assets/boards/{self.theme}.png")
        self.board = pygame.transform.scale(self.board, (HEIGHT, WIDTH))
        # self.board_scale = self.get_board_scale()

    # def get_board_scale(self):
        # return width / self.board_image.get_width()

    def draw_background(self):
        self.screen.blit(self.board, (0, 0))



    def handle_click_event(self, mouse_pos):

        return (
            int((mouse_pos[0] / SQUARE_SIZE)),
            int((mouse_pos[1] / SQUARE_SIZE))
        )
