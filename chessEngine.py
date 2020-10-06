class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False
        self.stale_mate = False
        self.enpassant_possible = ()
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_right_log = [CastleRights(self.current_castling_rights.wks,self.current_castling_rights.bks, 
                                            self.current_castling_rights.wqs,self.current_castling_rights.bqs)]


    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # update king's position
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        if move.piece_moved == "bK":
            self.white_black_location = (move.end_row, move.end_col)
        
        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # en-passant 
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--' # capturing pawn

        # update enpassant_possible
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2: # only when pawn moves two squere
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.end_col)
            print(self.enpassant_possible)
        else:
            self.enpassant_possible = ()
        
        if move.is_castle_moves:
            if move.end_col - move.start_col == 2: # king side castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.endcol + 1] # moves the rook
                self.board[move.end_row][move.end_col - 1] = '--' # erase old rook
            else: # queenside
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.endcol - 2]
                self.board[move.end_row][move.end_col - 2] = '--' # erase old rook
        # update castling rights wheter it is rook or king move
        print(self.current_castling_rights.wks)
        self.update_castle_right(move)
        self.castle_right_log.append(CastleRights(self.current_castling_rights.wks,self.current_castling_rights.bks, 
                                            self.current_castling_rights.wqs,self.current_castling_rights.bqs))

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # update king's position
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            if move.piece_moved == "bK":
                self.white_black_location = (move.start_row, move.start_col)
            # enpassant 
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--' # blank squere witch enpassant captueret previously
                # test if needed??
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()
            #undo castling rights 
            self.castle_right_log.pop()
            self.current_castling_rights = self.castle_right_log[-1]
            #undo castle move
            if move.is_castle_moves: #kingside
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else: #queenside
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

    def update_castle_right(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.wqs == False
                if move.start_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.bqs == False
                if move.start_col == 7:
                    self.current_castling_rights.bks = False
            
    '''
    all moves considering checks 
    # simple algoritm but not very efficent
    1) generate all possible moves
    2) gor each move, make the move
    3) generate all opponent's moves
    4) for each of your opponent's moves, see if they attack your king
    5) if they do, it is not a valid move
    '''
    def get_valid_moves(self):
        #save it in case of undoing move
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks, self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        print('prawda:   +_ ', temp_castle_rights.wks)
        # 1)
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        # 2)
        for i in range(len(moves) -1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i]) # 5)
            self.white_to_move = not self.white_to_move
            self.undo_move()
        if len(moves) == 0:
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True
        else: # if undo move 
            self.check_mate = False
            self.stale_mate = False
        
        self.enpassant_possible = temp_enpassant_possible 
        self.current_castling_rights = temp_castle_rights
        print('dada ', self.current_castling_rights.wks)
        return moves

    ''' 
    determine if the current player is in check
    '''
    def in_check(self):
        if self.white_to_move:
            return self.squere_under_attack(self.white_king_location[0], self.white_king_location[1])
        else: 
            return self.squere_under_attack(self.black_king_location[0], self.black_king_location[1])

    def squere_under_attack(self, row, col):
        self.white_to_move = not self.white_to_move # switch to opponent's turn
        opps_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move # switch turns back
        for move in opps_moves:
            if move.end_row == row and move.end_col == col:
               return True
        return False
    
    '''
    all moves without checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)): # retruns 8 in case to play on larger board :)
            for col in range(len(self.board[row])): # returns 8
                turn_color = self.board[row][col][0]
                if (turn_color == 'w' and self.white_to_move) or (turn_color == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    if piece == 'p':
                        self.get_pawn_moves(row, col, moves)
                    elif piece == 'R':
                        self.get_rook_moves(row, col, moves)
                    elif piece == 'B':
                        self.get_bishop_moves(row, col, moves)
                    elif piece == "Q":
                        self.get_queen_moves(row, col, moves)
                    elif piece == "K":
                        self.get_king_moves(row, col, moves)
                    elif piece == "N":
                        self.get_knight_moves(row, col, moves)
        return moves                        
    '''
    PAWN MOVES
    '''
    def get_pawn_moves(self, row, col, moves):
        # white pawns
        if self.white_to_move:
            if self.board[row - 1][col] == '--':
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == '--':
                    moves.append(Move((row, col), (row - 2, col), self.board))
            # captures
            if  col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col -1), self.board))
                elif (row - 1, col - 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row - 1, col -1), self.board, is_enpassant_move = True))
                    print("trigger wp r-1 c-1")
            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, is_enpassant_move = True))
                    print("trigger wp r-1 c+1")
        # black pawns
        if not self.white_to_move:
            if self.board[row + 1][col] == '--':
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == '--':
                    moves.append(Move((row, col), (row + 2, col), self.board))
            # captures
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row + 1, col -1), self.board, is_enpassant_move = True))
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, is_enpassant_move = True))
    '''
    ROOK MOVES, for better solution look at get_knight_moves
    '''    
    def get_rook_moves(self, row, col, moves):
        # north
        i = row - 1
        while i > 0:
            if (self.white_to_move and self.board[i][col][0] == 'w') or (not self.white_to_move and self.board[i][col][0] == 'b'):
                break
            elif (self.white_to_move and self.board[i][col][0] == 'b') or (not self.white_to_move and self.board[i][col][0] == 'w'):
                moves.append(Move((row, col), (i, col), self.board))
                break
            elif self.board[i][col] == '--':
                moves.append(Move((row, col), (i, col), self.board))
            i -= 1
        # south 
        j = row + 1
        while j <= 7:
            if (self.white_to_move and self.board[j][col][0] == 'w') or (not self.white_to_move and self.board[j][col][0] == 'b'):
                break
            elif (self.white_to_move and self.board[j][col][0] == 'b') or (not self.white_to_move and self.board[j][col][0] == 'w'):
                moves.append(Move((row, col), (j, col), self.board))
                break
            elif self.board[j][col] == '--':
                moves.append(Move((row, col), (j, col), self.board))
            j += 1
        # west 
        k = col - 1
        while k >= 0:
            if (self.white_to_move and self.board[row][k][0] == 'w') or (not self.white_to_move and self.board[row][k][0] == 'b'):
                break
            elif (self.white_to_move and self.board[row][k][0] == 'b') or (not self.white_to_move and self.board[row][k][0] == 'w'):
                moves.append(Move((row, col), (row, k), self.board))
                break
            elif self.board[row][k] == '--':
                moves.append(Move((row, col), (row, k), self.board))
            k -= 1
        # east
        l = col + 1
        while l <= 7:
            if (self.white_to_move and self.board[row][l][0] == 'w') or (not self.white_to_move and self.board[row][l][0] == 'b'):
                break
            elif (self.white_to_move and self.board[row][l][0] == 'b') or (not self.white_to_move and self.board[row][l][0] == 'w'):
                moves.append(Move((row, col), (row, l), self.board))
                break
            elif self.board[row][l] == '--':
                moves.append(Move((row, col), (row, l), self.board))
            l += 1
    '''
    BISHOP MOVES, for better solution look at get_knight_moves
    '''
    def get_bishop_moves(self, row, col, moves):
        # north-west
        i = 1
        while row - i >= 0 or col - i >= 0:
            if (self.white_to_move and self.board[row - i][col - i][0] == 'w') or (not self.white_to_move and self.board[row - i][col - i][0] == 'b'):
                break
            elif (self.white_to_move and self.board[row - i][col - i][0] == 'b') or (not self.white_to_move and self.board[row - i][col - i][0] == 'w'):
                moves.append(Move((row, col), (row - i, col - i), self.board))
                break
            elif self.board[row - i][col - i] == '--':
                moves.append(Move((row, col), (row - i, col - i), self.board))
            i += 1
        # north-east
        i = 1
        while row - i >= 0 and col + i <= 7:
            if (self.white_to_move and self.board[row - i][col + i][0] == 'w') or (not self.white_to_move and self.board[row - i][col + i][0] == 'b'):
                break
            elif (self.white_to_move and self.board[row - i][col + i][0] == 'b') or (not self.white_to_move and self.board[row - i][col + i][0] == 'w'):
                moves.append(Move((row, col), (row - i, col + i), self.board))
                break
            elif self.board[row - i][col - i] == '--':
                moves.append(Move((row, col), (row - i, col + i), self.board))
            i += 1
        # south-east
        i = 1
        while row + i <= 7 and col + i <= 7:
            if (self.white_to_move and self.board[row + i][col + i][0] == 'w') or (not self.white_to_move and self.board[row + i][col + i][0] == 'b'):
                break
            elif (self.white_to_move and self.board[row + i][col + i][0] == 'b') or (not self.white_to_move and self.board[row + i][col + i][0] == 'w'):
                moves.append(Move((row, col), (row + i, col + i), self.board))
                break
            elif self.board[row + i][col + i] == '--':
                moves.append(Move((row, col), (row + i, col + i), self.board))
            i += 1
        # south west
        i = 1
        while row + i <= 7 and col - i >= 0:
            if (self.white_to_move and self.board[row + i][col - i][0] == 'w') or (not self.white_to_move and self.board[row + i][col - i][0] == 'b'):
                break
            elif (self.white_to_move and self.board[row + i][col - i][0] == 'b') or (not self.white_to_move and self.board[row + i][col - i][0] == 'w'):
                moves.append(Move((row, col), (row + i, col - i), self.board))
                break
            elif self.board[row + i][col - i] == '--':
                moves.append(Move((row, col), (row + i, col - i), self.board))
            i += 1
    '''
    QUEEN MOVES
    '''
    def get_queen_moves(self, row, col, moves):
        self.get_bishop_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    '''
    KING MOVES, for better solution look at get_knight_moves
    '''
    def get_king_moves(self, row, col, moves):
        directions = ((1,0), (-1,0), (0,1),(0,-1),(-1, -1),(-1, 1),(1, -1), (1, 1))
        if self.white_to_move:
            enemy_color = "b"
        else:
            enemy_color = "w"
        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8: # on board
                end_piece = self.board[end_row][end_col]
                if end_piece == '--': # free piece
                    moves.append(Move((row, col), (end_row, end_col), self.board))
                elif end_piece[0] == enemy_color: # enemy piece
                    moves.append(Move((row, col), (end_row, end_col), self.board))
    '''
    KNIGHT MOVES
    '''
    def get_knight_moves(self, row, col, moves):
        directions = ((-1,2), (-2,-1), (-2, 1),(-1,-2 ),(1, 2),(2, 1),(2, -1), (1, -2))
        if self.white_to_move:
            ally_color = "w"
        else:
            ally_color = "b"
        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8: # on board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # enemy or empty
                    moves.append(Move((row, col), (end_row, end_col), self.board))



    def get_castle_moves(self, row, col, moves):
        if self.squere_under_attack(row, col):
            return
        if (self.white_to_move and self.current_castling_rights.wks) and (not self.white_to_move and self.current_castling_rights.bks):
            self.get_king_side_castle_moves(row, col, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) and (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_king_side_castle_moves(row, col, moves)
    
    def get_king_side_castle_moves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squere_under_attack(row, c+1) and not self.squere_under_attack(row, col+ 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_moves = True))
                print('mozesz na prwno')
        print('mozesz')
    
    def get_queen_side_castle_moves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squere_under_attack(row, c - 1) and not self.squere_under_attack(row, col - 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_moves = True))
    

class CastleRights():
    # wks - white king side, bqs - black queen side etc
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, 
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_rank = {v: k for k, v in ranks_to_rows.items()} # reverse dictionary eg. without it "1": 7 with it 7: "1"
    files_to_cols = {"A": 0, "B": 1, "C": 2, "D": 3,
                    "E": 4, "F": 5, "G": 6, "H": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_squere, end_squere, board, is_enpassant_move = False, is_castle_moves = False):
        self.start_row = start_squere[0]
        self.start_col = start_squere[1]
        self.end_row = end_squere[0]
        self.end_col = end_squere[1]
        self.piece_moved = board[self.start_row][self.start_col]  
        self.piece_captured = board[self.end_row][self.end_col]
        # pawn promotion
        self.is_pawn_promotion = False
        if (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7):
            self.is_pawn_promotion = True
        # en-passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'
        # castle move
        self.is_castle_moves = is_castle_moves
        # move ID
        self.moveID = self.start_row * 1000 + self.end_row * 100 + self.start_col * 10 + self.end_col


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
        
    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col) 

    def get_rank_file(self, row, col):
        return self.cols_to_files(col) + self.rows_to_rank(row)