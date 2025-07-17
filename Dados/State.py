class State:

    __slots__ = ('board', 'possibleMoves', 'heights', 'player', 'winner', 'row', 'col')

    def __init__(self):
        self.board = [[0]*7 for _ in range(6)]
        self.possibleMoves = list(range(7))
        self.heights = [5]*7
        self.player = 1
        self.winner = -1
        self.row = -1
        self.col = -1

    def copy(self):
        new_state = State()
        new_state.board = [row[:] for row in self.board]
        new_state.possibleMoves = self.possibleMoves[:]
        new_state.heights = self.heights[:]
        new_state.player = self.player
        new_state.winner = self.winner
        new_state.row = self.row
        new_state.col = self.col
        return new_state

    def move(self, column):
        row = self.heights[column]
        self.board[row][column] = self.player

        if row == 0:self.possibleMoves.remove(column)
        else:self.heights[column] = row - 1

        self.updateWinner(column, row)
        self.row = row
        self.col = column
        self.player = 3 - self.player

    def verifyMove(self,col):
        return col in self.possibleMoves

    def updateWinner(self,col,row):
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

