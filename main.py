import pygame

from src.constants import FPS, HEIGHT, WIDTH
from src.board import Board
from src.figures import Figures
from src.audio import Audio






pygame.init()
audio = Audio()
screen = pygame.display.set_mode([HEIGHT, WIDTH])
pygame.display.set_caption("Chess 0.01")
icon = pygame.image.load("./assets/icon.png")
pygame.display.set_icon(icon)



running = True
clock = pygame.time.Clock()
board = Board(screen)
figures = Figures(screen, audio)
figures.generate_default_board()
audio.play("game-start")
while running:
    clock.tick(FPS)

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = board.handle_click_event(pygame.mouse.get_pos())
            figures.handle_click_location(pos)
        if event.type == pygame.MOUSEMOTION:
            pos = board.handle_click_event(pygame.mouse.get_pos())
            draw_cursor = figures.handle_mouse_motion(pos, pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONUP:
            figures.handle_mouse_up(pos)
        
        #if R button is pressed, reset the board
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                board = Board(screen)
                figures = Figures(screen, audio)
                figures.generate_default_board()
                audio.play("game-start")
            if event.key == pygame.K_ESCAPE:
                running = False

    board.draw_background()
    figures.display_selected()
    figures.display_legal_moves()
    figures.display_figures()
    figures.disaply_promotion_ui()
    

    pygame.display.update()

