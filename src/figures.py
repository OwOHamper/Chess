import pygame
import os.path

from src.constants import *

class Figures():
    def __init__(self, screen, audio):
        self.screen = screen
        self.audio = audio
        self.theme = "neo"
        self.board = [["" for i in range(8)] for i in range(8)]
        self.figures = {}
        for color in ["w", "b"]:
            for piece in ["k", "q", "p", "n", "b", "r"]:
                self.figures[color + piece] = pygame.transform.scale(
                        pygame.image.load(f"./assets/pieces/{self.theme}/{color}{piece}.png"), 
                        (SQUARE_SIZE, SQUARE_SIZE)
                    )
        self.legal_move_circle = pygame.transform.scale(
            pygame.image.load("./assets/legal_move_circle.png"),(SQUARE_SIZE, SQUARE_SIZE)).convert_alpha()
        self.legal_move_circle.set_alpha(100)
        self.legal_move_figure_circle = pygame.transform.scale(
            pygame.image.load("./assets/legal_move_figure_circle.png"),(SQUARE_SIZE, SQUARE_SIZE)).convert_alpha()
        self.legal_move_figure_circle.set_alpha(100)
        self.currently_selected = None
        self.current_legal_moves = None
        self.last_selected = None
        self.last_move = None
        #color of ally figures
        self.client_color = "w"
        if self.client_color == "w":
            self.opponent_color = "b"
        else:
            self.opponent_color = "w"
        self.mouse_pos = None
        #drag and drop mode and click move mode
        self.click_move_mode = False
        self.move_done = False

        # self.duck = pygame.transform.scale(pygame.image.load("./assets/cursors/duck.png"), (SQUARE_SIZE, SQUARE_SIZE))
        self.render_on_top = None
        self.disable_currently_selected = False
        self.castle_available = {"w": {"k": True, "r": {0: True, 7: True}}, "b": {"k": True, "r": {0: True, 7: True}}}
        self.promote_ui_active = False
        self.promote_ui_pos = None
        self.client_promote = None
        self.promote_order = ["q", "n", "r", "b"]
        self.white_to_move = True


    def generate_default_board(self):
        #pawns
        for i in range(8):
            self.board[-2][i] = "wp"
            self.board[1][i] = "bp"

        #rooks
        self.board[-1][0] = "wr"
        self.board[-1][-1] = "wr"
        self.board[0][0] = "br"
        self.board[0][-1] = "br"

        #knights
        self.board[-1][1] = "wn"
        self.board[-1][-2] = "wn"
        self.board[0][1] = "bn"
        self.board[0][-2] = "bn"

        #bishops
        self.board[-1][2] = "wb"
        self.board[-1][-3] = "wb"
        self.board[0][2] = "bb"
        self.board[0][-3] = "bb"

        #queen
        self.board[-1][3] = "wq"
        self.board[0][3] = "bq"

        #king
        self.board[-1][4] = "wk"
        self.board[0][4] = "bk"


    def display_figures(self):
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                if self.board[row][col] != "":
                    if self.currently_selected != None and self.currently_selected == (row, col):
                        if self.mouse_pos != None:
                            self.render_on_top = (self.figures[self.board[row][col]], [self.mouse_pos[0] - SQUARE_SIZE / 2, self.mouse_pos[1] - SQUARE_SIZE / 2])
                        else:
                            self.screen.blit(self.figures[self.board[row][col]], (SQUARE_SIZE * col, SQUARE_SIZE * row))
                            
                    else:
                        self.screen.blit(self.figures[self.board[row][col]], (SQUARE_SIZE * col, SQUARE_SIZE * row))

        if self.render_on_top != None:
            self.screen.blit(self.render_on_top[0], self.render_on_top[1])
            self.render_on_top = None
    def display_selected(self):
        if self.currently_selected != None:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(150)
            s.fill(HIGHLIGHT_COLOR)
            self.screen.blit(s, (self.currently_selected[1] * SQUARE_SIZE, self.currently_selected[0] * SQUARE_SIZE))
        if self.last_move != None:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(150)
            s.fill(HIGHLIGHT_COLOR)
            self.screen.blit(s, (self.last_move[0][1] * SQUARE_SIZE, self.last_move[0][0] * SQUARE_SIZE))
            self.screen.blit(s, (self.last_move[1][1] * SQUARE_SIZE, self.last_move[1][0] * SQUARE_SIZE))

    def handle_click_location(self, pos):
        if self.promote_ui_active:
            self.select_promotion(pos[::-1])
            return
        self.move_done = False
        if pos != None:
            self.currently_selected = (pos[1], pos[0])
            self.current_legal_moves = self.check_legal_moves(self.currently_selected)

            #if square is selected and then moved to another square last selected needs to be empty in order to be able
            #to deselect the square so the last loc is stored in temp variable 
            #handle figure location move
            if self.last_selected != None and self.last_selected != self.currently_selected and self.last_selected != None:
                #prevent moving nothing to something
                if self.board[self.last_selected[0]][self.last_selected[1]] != "":
                    legal_moves = self.check_legal_moves(self.last_selected)
                    # print(self.board[self.last_selected[0]][self.last_selected[1]])
                    # print(self.currently_selected)
                    if self.currently_selected in legal_moves:
                        #move figure to new location
                        captured_piece = self.board[self.currently_selected[0]][self.currently_selected[1]]
                        moved_piece = self.board[self.last_selected[0]][self.last_selected[1]]
                        self.board[self.currently_selected[0]][self.currently_selected[1]] = moved_piece
                        #reset old location
                        self.board[self.last_selected[0]][self.last_selected[1]] = ""
                        #resets pointer

                        #PUT HERE MOVE EVENTS (AFTER MOVE IS MADE)
                        pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
                        #check for castle
                        king_squares_diff = self.last_selected[1] - self.currently_selected[1]
                        play_move_sound = True
                        if moved_piece[1] == "k" and abs(king_squares_diff) == 2:
                            play_move_sound = False
                            self.audio.play("castle")
                            if king_squares_diff == 2:
                                #castle queenside/long
                                self.board[self.currently_selected[0]][self.currently_selected[1] + 1] = self.board[self.currently_selected[0]][self.currently_selected[1] - 2]
                                self.board[self.currently_selected[0]][self.currently_selected[1] - 2] = ""
                            else:
                                #castle kingside/short
                                self.board[self.currently_selected[0]][self.currently_selected[1] - 1] = self.board[self.currently_selected[0]][self.currently_selected[1] + 1]
                                self.board[self.currently_selected[0]][self.currently_selected[1] + 1] = ""
                        
                        #check for pawn promotion
                        if moved_piece[1] == "p":
                            if self.currently_selected[0] == 0 or self.currently_selected[0] == 7:
                                #need to play sound later
                                play_move_sound = False
                                if self.client_color == moved_piece[0]:
                                    self.client_promote = True
                                else:
                                    self.client_promote = False
                                self.promote_ui_active = True
                                self.promote_ui_pos = self.currently_selected
                                # self.board[self.currently_selected[0]][self.currently_selected[1]] = moved_piece[0] + "q"

                        #check for en passant
                        if moved_piece[1] == "p":
                            if moved_piece[0] == self.client_color:
                                if abs(self.currently_selected[1] - self.last_selected[1]) and captured_piece == "":
                                    captured_piece = self.board[self.currently_selected[0]+1][self.currently_selected[1]]
                                    self.board[self.currently_selected[0]+1][self.currently_selected[1]] = ""
                            else:
                                if abs(self.currently_selected[1] - self.last_selected[1]) and captured_piece == "":
                                    captured_piece = self.board[self.currently_selected[0]-1][self.currently_selected[1]]
                                    self.board[self.currently_selected[0]-1][self.currently_selected[1]] = ""

                        if play_move_sound:
                            if self.client_color == self.board[self.currently_selected[0]][self.currently_selected[1]][0]:
                                if captured_piece != "":
                                    self.audio.play("capture")
                                else:
                                    self.audio.play("move-self")
                            else:
                                if captured_piece != "":
                                    self.audio.play("capture")
                                else:
                                    self.audio.play("move-opponent")


                        self.last_move = [self.last_selected, self.currently_selected]

                        match moved_piece[1]:
                            case "r":
                                self.castle_available[moved_piece[0]]["r"][self.last_selected[1]] = False
                            case "k":
                                self.castle_available[moved_piece[0]]["k"] = False

                        self.move_done = True
                        self.mouse_pos = None
                        self.click_move_mode = False
                        self.currently_selected = None
                        self.white_to_move = not self.white_to_move
                    else:
                        #illegal move, fixes a bug where if you move piece to another piece that piece will be selected
                        self.currently_selected = None
                        self.click_move_mode = False


        if self.currently_selected == self.last_selected:
            self.last_selected = None
            self.disable_currently_selected = True
            self.click_move_mode = False
        else:
            self.last_selected = self.currently_selected
        if self.currently_selected != None:
            if self.board[self.currently_selected[0]][self.currently_selected[1]] == "":
                self.currently_selected = None


    def disaply_promotion_ui(self):
        if self.promote_ui_active:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(240)
            s.fill(PROMOTE_COLOR)
            self.screen.blit(s, (self.promote_ui_pos[1] * SQUARE_SIZE, self.promote_ui_pos[0] * SQUARE_SIZE))
            for i, figurine in enumerate(self.promote_order):
                
                if self.client_promote:
                    self.figures[self.client_color + figurine]
                    position = (self.promote_ui_pos[1] * SQUARE_SIZE, self.promote_ui_pos[0] * SQUARE_SIZE + i * SQUARE_SIZE)
                    self.screen.blit(s, position)
                    self.screen.blit(self.figures[self.client_color + figurine], position)
                else:
                    self.figures[self.opponent_color + figurine]
                    position = (self.promote_ui_pos[1] * SQUARE_SIZE, self.promote_ui_pos[0] * SQUARE_SIZE - i * SQUARE_SIZE)
                    self.screen.blit(s, position)
                    self.screen.blit(self.figures[self.opponent_color + figurine], position)


    def select_promotion(self, pos):
        if self.promote_ui_active:
            if self.client_promote:
                if pos in [(self.promote_ui_pos[0]+i, self.promote_ui_pos[1]) for i in range(4)]:
                    self.board[self.promote_ui_pos[0]][self.promote_ui_pos[1]] = self.client_color + self.promote_order[pos[0] - self.promote_ui_pos[0]]
                    self.promote_ui_active = False
                    self.audio.play("promote")
            else:
                if pos in [(self.promote_ui_pos[0]-i, self.promote_ui_pos[1]) for i in range(4)]:
                    self.board[self.promote_ui_pos[0]][self.promote_ui_pos[1]] = self.opponent_color + self.promote_order[self.promote_ui_pos[0] - pos[0]]
                    self.promote_ui_active = False
                    self.audio.play("promote")


    def handle_mouse_motion(self, pos, mouse_pos):
        #changing cursors part
        if pos != None:
            if self.board[pos[1]][pos[0]] != "" or self.mouse_pos != None:
                pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
            else:
                #change cursors for promotion ui
                if self.promote_ui_active:
                    if pos in [(self.promote_ui_pos[1],self.promote_ui_pos[0] + i) for i in range(4)]:
                        pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
                    else:
                        pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
                else:
                    pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))

        if self.currently_selected != None and not self.click_move_mode:
            self.mouse_pos = mouse_pos
    
    def display_legal_moves(self):
        if self.currently_selected != None:
            for move in self.current_legal_moves:
                if self.board[move[0]][move[1]] == "":
                    self.screen.blit(self.legal_move_circle, (move[1] * SQUARE_SIZE, move[0] * SQUARE_SIZE))
                else:
                    self.screen.blit(self.legal_move_figure_circle, (move[1] * SQUARE_SIZE, move[0] * SQUARE_SIZE))

    def handle_mouse_up(self, pos):
        self.mouse_pos = None
        pos = (pos[1], pos[0])

        #released on same square
        if self.currently_selected == pos:
            # print("Same")
            #disables moving piece with mouse
            if self.disable_currently_selected:
                self.disable_currently_selected = False
                self.currently_selected = None
                return
            self.click_move_mode = True
            self.currently_selected = pos
            
        #released on different square
        if self.currently_selected != None and self.currently_selected != pos and not self.move_done:
            # print("different")
            self.disable_currently_selected = False
            self.handle_click_location(pos[::-1])

    def check_legal_moves(self, pos):
        piece = self.board[pos[0]][pos[1]]
        legal_moves = None
        if piece != "":
            if self.white_to_move and piece[0] != "w":
                return []
            elif not self.white_to_move and piece[0] != "b":
                return []
            if piece[0] == self.client_color:
                if piece[1] == "p":
                    legal_moves = self.check_pawn_moves(pos)
                elif piece[1] == "r":
                    legal_moves = self.check_rook_moves(pos)
                elif piece[1] == "n":
                    legal_moves = self.check_knight_moves(pos)
                elif piece[1] == "b":
                    legal_moves = self.check_bishop_moves(pos)
                elif piece[1] == "q":
                    legal_moves = self.check_queen_moves(pos)
                elif piece[1] == "k":
                    legal_moves = self.check_king_moves(pos)
            else:
                if piece[1] == "p":
                    legal_moves = self.check_pawn_moves(pos, black=True)
                elif piece[1] == "r":
                    legal_moves = self.check_rook_moves(pos, black=True)
                elif piece[1] == "n":
                    legal_moves = self.check_knight_moves(pos, black=True)
                elif piece[1] == "b":
                    legal_moves = self.check_bishop_moves(pos, black=True)
                elif piece[1] == "q":
                    legal_moves = self.check_queen_moves(pos, black=True)
                elif piece[1] == "k":
                    legal_moves = self.check_king_moves(pos, black=True)
        
        if legal_moves != None:
            return legal_moves
        return []

    def check_pawn_moves(self, pos, black=False):
        legal_moves = []
        # double move forward at start
        if not black:
            if pos[0] == 6:
                if self.board[pos[0] - 1][pos[1]] == "" and self.board[pos[0] - 2][pos[1]] == "":
                    legal_moves.append((pos[0] - 2, pos[1]))

            # single move forward
            if self.board[pos[0] - 1][pos[1]] == "":
                legal_moves.append((pos[0] - 1, pos[1]))

            # capturing
            if self.board[pos[0] - 1][pos[1] - 1] != "" and self.board[pos[0] - 1][pos[1] - 1][0] != self.client_color:
                legal_moves.append((pos[0] - 1, pos[1] - 1))
            if pos[1] < 7:
                if self.board[pos[0] - 1][pos[1] + 1] != "" and self.board[pos[0] - 1][pos[1] + 1][0] != self.client_color:
                    legal_moves.append((pos[0] - 1, pos[1] + 1))

            #en passant
            if pos[0] == 3:
                if pos[0] > 0:
                    left_pawn = self.board[pos[0]][pos[1]-1]
                    if left_pawn != "":
                        if left_pawn[0] != self.client_color and left_pawn[1] == "p":
                            if self.last_move == [(1, pos[1]-1), (3, pos[1]-1)]:
                                legal_moves.append((pos[0] - 1, pos[1] - 1))

                if pos[1] < 7:
                    right_pawn = self.board[pos[0]][pos[1]+1]
                    if right_pawn != "":
                        if right_pawn[0] != self.client_color and right_pawn[1] == "p":
                            if self.last_move == [(1, pos[1]+1), (3, pos[1]+1)]:
                                legal_moves.append((pos[0] - 1, pos[1] + 1))
        else:
            if pos[0] == 1:
                if self.board[pos[0] + 1][pos[1]] == "" and self.board[pos[0] + 2][pos[1]] == "":
                    legal_moves.append((pos[0] + 2, pos[1]))

            # single move forward
            if self.board[pos[0] + 1][pos[1]] == "":
                legal_moves.append((pos[0] + 1, pos[1]))

            # capturing
            if self.board[pos[0] + 1][pos[1] - 1] != "" and self.board[pos[0] + 1][pos[1] - 1][0] == self.client_color:
                legal_moves.append((pos[0] + 1, pos[1] - 1))
            if pos[1] < 7:
                if self.board[pos[0] + 1][pos[1] + 1] != "" and self.board[pos[0] + 1][pos[1] + 1][0] == self.client_color:
                    legal_moves.append((pos[0] + 1, pos[1] + 1))

            #en passant
            if pos[0] == 4:
                # if pos[0] > 0:
                left_pawn = self.board[pos[0]][pos[1]-1]
                if left_pawn != "":
                    if left_pawn[0] == self.client_color and left_pawn[1] == "p":
                        if self.last_move == [(6, pos[1]-1), (4, pos[1]-1)]:
                            legal_moves.append((pos[0] + 1, pos[1] - 1))

                if pos[1] < 7:
                    right_pawn = self.board[pos[0]][pos[1]+1]
                    if right_pawn != "":
                        if right_pawn[0] == self.client_color and right_pawn[1] == "p":
                            if self.last_move == [(6, pos[1]+1), (4, pos[1]+1)]:
                                legal_moves.append((pos[0] + 1, pos[1] + 1))

        return legal_moves

    def check_rook_moves(self, pos, black=False):
        legal_moves = []
        # move_offsets = [(i, 0) for i in range(-7, 8)] + [(0, i) for i in range(-7, 8)]
        move_offsets = [
            [(i, 0) for i in range(-1, -8, -1)],
            [(i, 0) for i in range(1, 8)],
            [(0, i) for i in range(-1, -8, -1)],
            [(0, i) for i in range(1, 8)],
        ]
        for direction in move_offsets:
            for offset in direction:
                new_pos = (pos[0] + offset[0], pos[1] + offset[1])
                if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:
                    destination = self.board[new_pos[0]][new_pos[1]]
                    if destination != "":
                        if black:
                            if destination[0] == self.opponent_color:
                                break
                        else:
                            if destination[0] == self.client_color:
                                break
                        legal_moves.append(new_pos)
                        break
                    legal_moves.append(new_pos)

        return legal_moves

    def check_knight_moves(self, pos, black=False):
        legal_moves = []
        
        move_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for offset in move_offsets:
            new_pos = (pos[0] + offset[0], pos[1] + offset[1])
            if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:
                destination = self.board[new_pos[0]][new_pos[1]]
                if destination != "":
                    if black:
                        if destination[0] == self.opponent_color:
                            continue
                    else:
                        if destination[0] == self.client_color:
                            continue
                legal_moves.append(new_pos)

        return legal_moves

    def check_bishop_moves(self, pos, black=False):
        legal_moves = []
        move_offsets = [
            [(i, i) for i in range(-1, -8, -1)],
            [(i, i) for i in range(1, 8)],
            [(i, -i) for i in range(-1, -8, -1)],
            [(i, -i) for i in range(1, 8)],
        ]
        for direction in move_offsets:
            for offset in direction:
                new_pos = (pos[0] + offset[0], pos[1] + offset[1])
                if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:
                    destination = self.board[new_pos[0]][new_pos[1]]
                    if destination != "":
                        if black:
                            if destination[0] == self.opponent_color:
                                break
                        else:
                            if destination[0] == self.client_color:
                                break
                        legal_moves.append(new_pos)
                        break
                    legal_moves.append(new_pos)

        return legal_moves

    def check_queen_moves(self, pos, black=False):
        legal_moves = []
        move_offsets = [
            [(i, 0) for i in range(-1, -8, -1)],
            [(i, 0) for i in range(1, 8)],
            [(0, i) for i in range(-1, -8, -1)],
            [(0, i) for i in range(1, 8)],
            [(i, i) for i in range(-1, -8, -1)],
            [(i, i) for i in range(1, 8)],
            [(i, -i) for i in range(-1, -8, -1)],
            [(i, -i) for i in range(1, 8)],
        ]
        for direction in move_offsets:
            for offset in direction:
                new_pos = (pos[0] + offset[0], pos[1] + offset[1])
                if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:
                    destination = self.board[new_pos[0]][new_pos[1]]
                    if destination != "":
                        if black:
                            if destination[0] == self.opponent_color:
                                break
                        else:
                            if destination[0] == self.client_color:
                                break
                        legal_moves.append(new_pos)
                        break
                    legal_moves.append(new_pos)

        return legal_moves

    def check_king_moves(self, pos, black=False):
        legal_moves = []
        move_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for offset in move_offsets:
            new_pos = (pos[0] + offset[0], pos[1] + offset[1])
            if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:
                destination = self.board[new_pos[0]][new_pos[1]]
                if destination != "":
                    if black:
                        if destination[0] == self.opponent_color:
                            continue
                    else:
                        if destination[0] == self.client_color:
                            continue
                legal_moves.append(new_pos)

        # castling
        # {'w': {'k': True, 'r': {0: True, 7: True}}}
        # check for pieces that they haven't moved
        if black:
            color = self.opponent_color
        else:
            color = self.client_color
        if self.castle_available[color]["k"] and self.castle_available[color]["r"][0] and self.castle_available[color]["r"][7]:
            # check for no check
            #todo
            if True:
                if self.board[pos[0]][pos[1] - 1] == "" and self.board[pos[0]][pos[1] - 2] == "" and self.board[pos[0]][pos[1] - 3] == "":
                    legal_moves.append((pos[0], pos[1] - 2))
                if self.board[pos[0]][pos[1] + 1] == "" and self.board[pos[0]][pos[1] + 2] == "":
                    legal_moves.append((pos[0], pos[1] + 2))


        return legal_moves