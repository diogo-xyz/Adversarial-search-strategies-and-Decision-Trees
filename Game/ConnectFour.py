from Game.Board import Board

class ConnectFour:
    """
    Controla o fluxo de jogo entre dois jogadores (humanos ou MCTS).
    """
    def __init__(self, funcPlayer1, funcPlayer2):
        """
        Inicializa uma nova partida de Connect Four.
        metros:
            funcPlayer1: Função que decide os movimentos do jogador 1.
            funcPlayer2: Função que decide os movimentos do jogador 2.
        """
        self.board = Board()
        self.player1 = funcPlayer1
        self.player2 = funcPlayer2
        self.player_input = None 

    def print_state(self):   
        """
        Exibe o estado atual do tabuleiro:
        - 'X' para o jogador 1
        - 'O' para o jogador 2
        - '-' para espaços vazios
        """
        for i in range(6):
            print("\t", end="")
            for j in range(7):
                piece = ""
                if (self.board.board[i][j]) == 1:
                    piece = "X"
                elif (self.board.board[i][j]) == 2:
                    piece = "O"
                else:
                    piece = "-"
                print("| " + str(piece), end=" ")
            print("|")
            
        print("\t+---+---+---+---+---+---+---+")
        print("\t  1   2   3   4   5   6   7 ")
        print()

    def simularJogo(self):
        """
        Executa uma jogada no jogo, se ele ainda estiver em andamento.

        A função do jogador correspondente ao turno atual é chamada para
        decidir a próxima jogada. Se a jogada for válida, ela é executada,
        o tabuleiro é atualizado e o novo estado é exibido.
        """
        if self.board.winner != -1:
            return
        
        if self.board.player == 1:
            move = self.player1(self)
        else:
            move = self.player2(self)

        if move is None:
            return

        if self.board.verifyMove(move):  
            self.board.move(move)
            self.print_state()
            self.player_input = None