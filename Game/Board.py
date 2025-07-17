class Board:
    """
    Representa o estado do jogo.

    A classe controla o tabuleiro, os movimentos possíveis, o jogador atual, 
    e determina se houve vitória ou empate após cada jogada.
    """
    __slots__ = ('board', 'possibleMoves', 'heights', 'player', 'winner', 'row', 'col')

    def __init__(self):
        """
        Inicializa um novo tabuleiro vazio de 6 linhas por 7 colunas.
        """
        self.board = [[0]*7 for _ in range(6)]
        self.possibleMoves = list(range(7))
        self.heights = [5]*7
        self.player = 1
        self.winner = -1
        self.row = -1
        self.col = -1

    def copy(self):
        """
        Devolve uma cópia do estado atual do tabuleiro.
        """
        new_state = Board()
        new_state.board = [row[:] for row in self.board]
        new_state.possibleMoves = self.possibleMoves[:]
        new_state.heights = self.heights[:]
        new_state.player = self.player
        new_state.winner = self.winner
        new_state.row = self.row
        new_state.col = self.col
        return new_state
    
    def move(self, column):
        """
        Realiza a jogada do jogador.
            column: índice da coluna onde será colocada a peça.
        """
        row = self.heights[column]
        self.board[row][column] = self.player

        if row == 0:self.possibleMoves.remove(column)
        else:self.heights[column] = row - 1

        self.updateWinner(column, row)
        self.row = row
        self.col = column
        self.player = 3 - self.player

    def verifyMove(self,col):
        """
        Verifica se uma jogada é válida na coluna especificada.
        """
        return col in self.possibleMoves

    def updateWinner(self,col,row):
        """
        Verifica se a jogada realizada gerou uma vitória.
        """
        directions = [(0,1),(1,0),(1,1),(1,-1)]

        for dirRow,dirCol in directions:
            count = 1

            i = 1
            while (0 <= row + i * dirRow < len(self.board) and 0 <= col + i * dirCol < len(self.board[0])):
                if(self.board[row][col] == self.board[row + i * dirRow ][col + i * dirCol]): 
                    count += 1 
                    i += 1
                else: break
            
            i = 1
            while (0 <= row - i * dirRow < len(self.board) and 0 <= col - i * dirCol < len(self.board[0])):
                if(self.board[row][col] == self.board[row - i * dirRow ][col - i * dirCol]): 
                    count +=1
                    i += 1
                else: break


            if(count >= 4): 
                self.winner = self.board[row][col]
                return

        if len(self.possibleMoves) == 0: self.winner = 0

    def winner_sequence(self,col,row):
        """
        Retorna a sequência de 4 ou mais peças que causaram a vitória.
            col: coluna da última peça jogada
            row: linha da última peça jogada

        Devolve um lista de tuple, que contém as coordenadas da sequência
        vencedora ou None se não houver vitória.
        """
        directions = [(0,1),(1,0),(1,1),(1,-1)]

        for dirRow,dirCol in directions:
            count = 1
            winningPieces = [(row, col)]

            i = 1
            while (0 <= row + i * dirRow < len(self.board) and 0 <= col + i * dirCol < len(self.board[0])):
                if(self.board[row][col] == self.board[row + i * dirRow ][col + i * dirCol]): 
                    count += 1 
                    winningPieces.insert(0, (row + i * dirRow, col + i * dirCol))                    
                    i += 1
                else: break
            
            i = 1
            while (0 <= row - i * dirRow < len(self.board) and 0 <= col - i * dirCol < len(self.board[0])):
                if(self.board[row][col] == self.board[row - i * dirRow ][col - i * dirCol]): 
                    count +=1
                    winningPieces.insert(0, (row - i * dirRow, col - i * dirCol))
                    i += 1
                else: break


            if(count >= 4): 
                return winningPieces

        return None
