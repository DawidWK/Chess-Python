import pygame
import chessEngine

# screen 
HEIGHT = WIDTH = 512
DIMENSION = 8

# images
IMAGES = {}

# colors 
WHITE = (214, 214, 214)
BLACK = (82, 48, 44)

# checkboard
SQUERE_SIZE = int(WIDTH / 8)

'''
loads images only once
'''
def load_images():
    pieces = ["bR","bB", "bK", "bN", "bp", "bQ", "wB", "wK", "wN", "wp", "wQ", "wR"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(f'images/{piece}.png'), (SQUERE_SIZE, SQUERE_SIZE))

'''
Highlight squere selecteda and valid moves
'''
def hightlight_squeres(screen, gs, valid_moves, squere_selected):
    if squere_selected != ():
        row, col = squere_selected
        if gs.board[row][col][0] == ('w' if gs.white_to_move else 'b'):
            s = pygame.Surface((SQUERE_SIZE, SQUERE_SIZE))
            s.set_alpha(100) # transparency if 0 = completly transparent max = 255
            s.fill(pygame.Color('blue'))
            screen.blit(s, (col*SQUERE_SIZE, row*SQUERE_SIZE))
            #higlight moves from that squere
            s.fill(pygame.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQUERE_SIZE, move.end_row * SQUERE_SIZE))



'''
handle current game state   
'''
def draw_game_state(screen, gs, valid_moves, squere_selected):
    draw_board(screen)
    hightlight_squeres(screen, gs, valid_moves, squere_selected)
    draw_pieces(screen, gs.board)


def draw_board(screen):    
    colors = [pygame.Color("white"), pygame.Color("grey")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(column * SQUERE_SIZE, row * SQUERE_SIZE, SQUERE_SIZE, SQUERE_SIZE))

def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(column * SQUERE_SIZE, row * SQUERE_SIZE, SQUERE_SIZE, SQUERE_SIZE))
    
def main():  
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BLACK) 
    gs = chessEngine.GameState()

    # to avoid generating every valid moves in every loop
    valid_moves = gs.get_valid_moves()
    move_made = False #flag variable for when a move is made

    load_images()
    running = True
    number_of_moves = 0
    squere_selected = () #keep track of last click 
    playerClicks = [] # keep track of player clicks eg. [(6, 4), (4, 4)]
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # mouse handlers
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos() # (x, y) location of mouse
                col = location[0]//SQUERE_SIZE # location[0] = x
                row =  location[1]//SQUERE_SIZE 
                if squere_selected == (row, col): # if user select same squere twice
                    squere_selected = () # unselect
                    playerClicks = []
                else:
                    squere_selected = (row, col)
                    playerClicks.append(squere_selected)

                if len(playerClicks) == 2: # after 2nd click
                    move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(playerClicks)
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            gs.make_move(valid_moves[i])
                            number_of_moves += 1
                            move_made = True
                            squere_selected = ()
                            playerClicks = []
                    if not move_made:
                        playerClicks = [squere_selected]
                        
            # undo handler
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z: # undo if z is pressed
                    gs.undo_move() 
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs, valid_moves, squere_selected)
        pygame.display.flip()
 
if __name__ == "__main__":
    main()