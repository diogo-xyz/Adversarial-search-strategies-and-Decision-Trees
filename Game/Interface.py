import sys
from joblib import load

from Game.Constants import *
from Game.InputBox import *
from Game.States import State, Algorithm

from Game.ConnectFour import ConnectFour
from Game.MCTS2 import MCTS2
from Game.MCTS3 import MCTS3
from Game.MCTSID3 import MCTSID3



class Interface:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Connect Four')

        self.backgroundImage1 = pygame.image.load('Game/Connect_4.png')
        self.backgroundImage1 = pygame.transform.scale(self.backgroundImage1, (WIDTH, HEIGHT))
        
        self.backgroundImage = pygame.image.load('Game/background.png')
        self.backgroundImage = pygame.transform.scale(self.backgroundImage, (WIDTH, HEIGHT)) 

        self.backgroundImage2 = pygame.image.load('Game/background3.png')
        self.backgroundImage2 = pygame.transform.scale(self.backgroundImage2, (WIDTH, HEIGHT))

        # Game icon
        icon = pygame.Surface((32, 32))
        icon.fill(BEIGE)
        pygame.draw.circle(icon, PINK, (16, 16), 15)
        pygame.display.set_icon(icon)
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.input_cooldown_until = 0

        # Game state
        self.state = State.MENU

        self.player1_type = None
        self.player2_type = None

        # Algorithm parameters
        self.mcts_time1 = 3  # Default MCTS time for player 1
        self.mcts_constant1 = 1.4142  # Default MCTS exploration constant for player 1
        self.mcts_time2 = 3  # Default MCTS time for player 2
        self.mcts_constant2 = 1.4142  # Default MCTS exploration constant for player 2

        # States for configuration
        self.configuring_player = None  # Which player we're configuring (1 or 2)

        # Create input boxes for parameters
        self.mcts_time_input = InputBox(WIDTH//2 - 50, HEIGHT//2 - 80, 200, 60, str(self.mcts_time1))
        self.mcts_constant_input = InputBox(WIDTH//2 - 50, HEIGHT//2 + 30, 200, 60, str(self.mcts_constant1))

        # Game mode and algorithm
        self.gameMode = None  # GameMode.PLAYER_VS_PLAYER, 'GameMode.PLAYER_VS_BOT, GameMode.BOT_VS_BOT
        
        # Create buttons
        self.playButton = Button(WIDTH//2 - 210, HEIGHT//2 + 200, 150, 70, 'Play', YELLOW, GREEN)
        self.rulesButton = Button(WIDTH//2 + 80, HEIGHT//2 - 300, 150, 70, 'Rules', LIGHT_CYAN, GRAY)
        self.backButton = Button(0, 0, 140, 50, 'Back', LIGHT_CYAN, GRAY)
        self.playAgainButton = Button(WIDTH//2 - 150, HEIGHT//2 - 40, 300, 70, 'Play Again', LIGHT_BLUE, BLUE)
        self.menuButton = Button(WIDTH//2 - 150, HEIGHT//2 + 60, 300, 70, 'Main Menu', LIGHT_CYAN, GRAY)
        
        self.backButton.rect.center = (WIDTH//2, HEIGHT//2 + 210)
        self.helpButton = Button(WIDTH - 230, 20, 50, 50, '?', PINK, GRAY)

        button_width = 140
        button_height = 50
        left_x = WIDTH // 4            
        right_x = 3 * WIDTH // 4       
        start_y = 200                  
        spacing = 70             

        # Player 1 buttons (left side)
        self.mcts2Button1 = Button(left_x, start_y + 0 * spacing, button_width, button_height, 'MCTS2', BLUE, LIGHT_CYAN)
        self.mcts3Button1 = Button(left_x, start_y + 1 * spacing, button_width, button_height, 'MCTS3', BLUE, LIGHT_CYAN)
        self.mctsid3Button1 = Button(left_x, start_y + 2 * spacing, button_width, button_height, 'MCTSID3',   BLUE, LIGHT_CYAN)
        self.humanButton1  = Button(left_x, start_y + 3 * spacing, button_width, button_height, 'Human',  BLUE, LIGHT_CYAN)

        # Player 2 buttons (right side)
        self.mcts2Button2 = Button(right_x, start_y + 0 * spacing, button_width, button_height, 'MCTS2', BLUE, LIGHT_CYAN)
        self.mcts3Button2 = Button(right_x, start_y + 1 * spacing, button_width, button_height, 'MCTS3', BLUE, LIGHT_CYAN)
        self.mctsid3Button2 = Button(right_x, start_y + 2 * spacing, button_width, button_height, 'MCTSID3',   BLUE, LIGHT_CYAN)
        self.humanButton2  = Button(right_x, start_y + 3 * spacing, button_width, button_height, 'Human',  BLUE, LIGHT_CYAN)

        # List of buttons for each player
        self.player1_buttons = [self.mcts2Button1, self.mcts3Button1, self.mctsid3Button1, self.humanButton1]
        self.player2_buttons = [self.mcts2Button2, self.mcts3Button2, self.mctsid3Button2, self.humanButton2]
        
        self.backButton2 = Button(0, 0, 100, 40, 'Back', LIGHT_CYAN, GRAY)
        self.startGameButton = Button(0, 0, button_width, button_height, 'Start', YELLOW, (0, 200, 0))
        self.confirmButton = Button(0, 0, 140, 50, 'Confirm', YELLOW, (0, 200, 0))

        self.backButton2.rect.center = (75 , 50)
        self.startGameButton.rect.center = (right_x - 175, HEIGHT - 50)
        self.confirmButton.rect.center = (right_x - 175, HEIGHT//2 + 240)

        self.panel_width = 400
        self.panel_height = 320
        self.panel_x = (WIDTH - self.panel_width) // 2
        self.panel_y = (HEIGHT - self.panel_height) // 2
        self.pauseButton = Button(WIDTH - 160, 20, 140, 50, 'Pause', LIGHT_CYAN, GRAY)
        self.resumeButton = Button(self.panel_x + 50, self.panel_y + 100, self.panel_width-100, 50, 'Resume', YELLOW, GREEN)
        self.restartButton = Button(self.panel_x + 50, self.panel_y + 170, self.panel_width-100, 50, 'Restart', LIGHT_CYAN, GRAY)
        self.pauseMenuButton = Button(self.panel_x + 50, self.panel_y + 240, self.panel_width-100, 50, 'Main Menu', LIGHT_CYAN, GRAY)
        
        # Fonts for messages
        self.textFont = pygame.font.Font(None, 40)
        self.titleFont = pygame.font.Font(None, 80)
        self.subtitleFont = pygame.font.Font(None, 60)

    def draw_menu(self):
        """Draws the main menu"""
        self.screen.blit(self.backgroundImage1, (0, 0))        
        self.playButton.draw(self.screen)
        self.rulesButton.draw(self.screen)

    def draw_algorithm_selection(self):
        """Draws the algorithm selection screen for each player"""
        self.screen.blit(self.backgroundImage, (0, 0))

        title1 = self.subtitleFont.render('Player 1', True, DARK_BLUE)
        title2 = self.subtitleFont.render('Player 2', True, DARK_BLUE)
        titleRect1 = title1.get_rect(center=(WIDTH // 3 - 10, HEIGHT // 8 + 50))
        titleRect2 = title2.get_rect(center=(2 * WIDTH // 3 + 10, HEIGHT // 8 + 50))
        self.screen.blit(title1, titleRect1)
        self.screen.blit(title2, titleRect2)

        button_spacing = 70
        start_y = HEIGHT // 8 + 180
        player1_x = WIDTH // 3 - 10
        player2_x = 2 * WIDTH // 3 + 10

        # Player 1 buttons
        for i, button in enumerate(self.player1_buttons): 
            button.rect.center = (player1_x, start_y + i * button_spacing)
            button.draw(self.screen)

        # Player 2 buttons
        for i, button in enumerate(self.player2_buttons): 
            button.rect.center = (player2_x, start_y + i * button_spacing)
            button.draw(self.screen)

        self.backButton2.draw(self.screen)
        self.startGameButton.draw(self.screen)

        # Display configuration info for each player
        selected1_lines = ["Selected:", str(self.player1_type) if self.player1_type else "-"]
        selected2_lines = ["Selected:", str(self.player2_type) if self.player2_type else "-"]
        
        if self.player1_type == Algorithm.MCTS2 or self.player1_type == Algorithm.MCTS3 or self.player1_type == Algorithm.MCTSID3:
            selected1_lines.append(f"Time: {self.mcts_time1}")
            selected1_lines.append(f"C: {self.mcts_constant1}")
            
        if self.player2_type == Algorithm.MCTS2 or self.player2_type == Algorithm.MCTS3 or self.player2_type == Algorithm.MCTSID3:
            selected2_lines.append(f"Time: {self.mcts_time2}")
            selected2_lines.append(f"C: {self.mcts_constant2}")
        
        x1 = WIDTH // 4 - 20
        y = HEIGHT // 8 + 500
        x2 = 3 * WIDTH // 5 - 10

        for i, line in enumerate(selected1_lines):
            rendered = self.textFont.render(line, True, DARK_BLUE)
            self.screen.blit(rendered, (x1, y + i * 30))

        for i, line in enumerate(selected2_lines):
            rendered = self.textFont.render(line, True, DARK_BLUE)
            self.screen.blit(rendered, (x2, y + i * 30))

    def draw_mcts_config(self):
        """Draw configuration screen for MCTS algorithm"""
        self.screen.blit(self.backgroundImage, (0, 0))
        
        player_num = "1" if self.configuring_player == 1 else "2"
        title = self.subtitleFont.render(f'MCTS Config - Player {player_num}', True, DARK_BLUE)
        titleRect = title.get_rect(center=(WIDTH//2, HEIGHT//5 - 10))
        self.screen.blit(title, titleRect)
        
        # Instructions
        instr1 = self.subtitleFont.render("Enter time (1-7):", True, DARK_BLUE)
        instr1_rect = instr1.get_rect(center=(WIDTH//2, HEIGHT//2 - 160))
        self.screen.blit(instr1, instr1_rect)
        
        
        instr2 = self.subtitleFont.render("Enter constant (1-7):", True, DARK_BLUE)
        instr2_rect = instr2.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(instr2, instr2_rect)
        
        # Draw input boxes
        self.mcts_time_input.rect.center = (WIDTH//2, HEIGHT//2 - 80)
        self.mcts_constant_input.rect.center = (WIDTH//2, HEIGHT//2 + 80)
        self.mcts_time_input.draw(self.screen)
        self.mcts_constant_input.draw(self.screen)
        
        # Draw confirm button
        self.confirmButton.draw(self.screen)
        self.backButton2.draw(self.screen)

    def draw_rules(self):
        """Draws the rules screen"""
        self.screen.blit(self.backgroundImage2, (0, 0))
                
        title = self.titleFont.render('Game Rules', True, DARK_BLUE)
        titleRect = title.get_rect(center=(WIDTH//2, HEIGHT // 8 + 50))
        self.screen.blit(title, titleRect)
        card_width = WIDTH * 0.75
        card_height = HEIGHT * 0.8
        card_x = (WIDTH - card_width) // 2
        card_y = (HEIGHT - card_height) // 2
        y_position = card_y + 190

        objective_title = self.textFont.render("OBJECTIVE", True, BLUE)
        self.screen.blit(objective_title, (card_x , card_y + 150))
        objective_text = [
            "Be the first player to connect 4 of the", 
            "same colored discs in a row (either",
            "vertically, horizontally or diagonally)."
        ]

        for line in objective_text:
            text = self.textFont.render(line, True, DARK_BLUE)
            self.screen.blit(text, (card_x + 5, y_position))
            y_position += 38
        
        # How to play section
        how_to_play = self.textFont.render("HOW TO PLAY", True, BLUE)
        self.screen.blit(how_to_play, (card_x , y_position + 20))
        
        # Rules list
        rules = [
            "* Players take turns dropping discs ","into the board.",
            "* Discs fall straight down to the lowest","available space.",
            "* The first player to form a line of 4","discs wins.",
            "* The game ends when the board is ","full (draw) or a player wins."
        ]
        
        y_position += 60
        for rule in rules:
            text = self.textFont.render(rule, True, DARK_BLUE)
            self.screen.blit(text, (card_x + 5, y_position))
            y_position += 38
            
        self.backButton2.draw(self.screen)

    def draw_pause_menu(self):
        self.draw_board()
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  
        self.screen.blit(overlay, (0, 0))

        pause_panel = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        pause_panel.fill((138, 199, 243, 230))  
        pygame.draw.rect(pause_panel, (255, 255, 255, 50), (0, 0, self.panel_width, self.panel_height), 5)
        
        title = self.titleFont.render("PAUSE", True, DARK_BLUE)
        titleRect = title.get_rect(center=(self.panel_width//2, 50))
        pause_panel.blit(title, titleRect)
        
        self.screen.blit(pause_panel, (self.panel_x, self.panel_y))

        self.resumeButton.draw(self.screen)
        self.restartButton.draw(self.screen)
        self.pauseMenuButton.draw(self.screen)

    def draw_pieces(self):
        # Draw board circles
        for c in range(COLUMNS):
            for r in range(ROWS):
                pygame.draw.rect(self.screen, DARK_BLUE, (c*SQUARE_SIZE, (r+1)*SQUARE_SIZE + 150, SQUARE_SIZE + 150, SQUARE_SIZE + 150))
                pygame.draw.circle(self.screen, WHITE, (int(c*SQUARE_SIZE + SQUARE_SIZE/2), int((r+1)*SQUARE_SIZE+ 150 + SQUARE_SIZE/2)), RADIUS)
        
        for c in range(COLUMNS):
            for r in range(ROWS):
                piece = self.game.board.board[r][c]
                if piece == 1:
                    color = GREEN
                elif piece == 2:
                    color = YELLOW
                else:
                    continue  

                pygame.draw.circle( self.screen, color, (int(c * SQUARE_SIZE + SQUARE_SIZE / 2), int((r + 1) * SQUARE_SIZE + 150 + SQUARE_SIZE / 2)), RADIUS)
        # Draw current player's piece at the top (if game not over)
        if self.game.board.winner == -1 and self.state != State.PAUSE:
            pos_x = pygame.mouse.get_pos()[0]
            column = min(max(0, int(pos_x // SQUARE_SIZE)), COLUMNS-1)  # Limit the column
            centered_pos_x = column * SQUARE_SIZE + SQUARE_SIZE//2
            pieceColor = GREEN if self.game.board.player == 1 else YELLOW
            pygame.draw.circle(self.screen, pieceColor, 
                (centered_pos_x, SQUARE_SIZE//2 + 150), RADIUS)
    
    def highlight_winner(self, column, row):
        """Highlights the winning pieces"""
        if self.game.board.winner > 0:
            winning_sequence = self.game.board.winner_sequence(column, row)
            for row, col in winning_sequence:
                pygame.draw.circle(self.screen, PINK, (int(col * SQUARE_SIZE + SQUARE_SIZE / 2), int((row + 1) * SQUARE_SIZE + 150 + SQUARE_SIZE / 2)), RADIUS)

    def draw_board(self):
        """Draws the game board and pieces"""
        # Blue background
        self.screen.fill(DARK_BLUE)
        self.pauseButton.draw(self.screen)
        self.helpButton.draw(self.screen)
        self.draw_pieces()
        # Game mode information
        infoFont = pygame.font.Font(None, 36)
        modeText = ""
        if self.player1_type == Algorithm.HUMAN and self.player2_type == Algorithm.HUMAN:
            modeText = "Mode: 1 vs 1"
        elif Algorithm.HUMAN in [self.player1_type, self.player2_type]:
            bot_type = self.player2_type if self.player1_type == Algorithm.HUMAN else self.player1_type
            modeText = f"Mode: 1 vs BOT ({bot_type})"
        else:
            modeText = f"Mode: BOT1 ({self.player1_type}) vs BOT2 ({self.player2_type})"

        infoText = infoFont.render(modeText, True, WHITE)
        self.screen.blit(infoText, (20, 20))

        # Display algorithm parameters if applicable
        param_y = 60
        
        if self.player1_type != Algorithm.HUMAN:
            param_text = infoFont.render(f"Green: {self.player1_type}, Time: {self.mcts_time1}, C: {self.mcts_constant1}", True, WHITE)
            self.screen.blit(param_text, (20, param_y))
            param_y += 40
            
        if self.player2_type != Algorithm.HUMAN:
            param_text = infoFont.render(f"Yellow: {self.player2_type}, Time: {self.mcts_time2}, C: {self.mcts_constant2}", True, WHITE)
            self.screen.blit(param_text, (20, param_y))
    
    def draw_end_screen(self):
        self.draw_board()
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  
        self.screen.blit(overlay, (0, 0))

        if self.game.board.winner == 0:
            winnerText = 'Draw!'
            panel_color = (*DARK_BLUE, 230)
            titleColor = WHITE
        else:
            winner = self.game.board.winner
            if winner == 1:
                panel_color = (*GREEN, 230)  
            elif winner == 2:
                panel_color = (*YELLOW, 230) 

            p1 = self.player1_type
            p2 = self.player2_type

            if p1 == Algorithm.HUMAN and p2 == Algorithm.HUMAN:
                winnerText = f"Player {winner} Won!"
            elif Algorithm.HUMAN in [p1, p2]:
                if (winner == 1 and p1 == Algorithm.HUMAN) or (winner == 2 and p2 == Algorithm.HUMAN):
                    winnerText = "You Won!"
                else:
                    bot_type = p2 if winner == 2 else p1
                    winnerText = f"{bot_type} Won!"
            else:
                winning_bot_type = p1 if winner == 1 else p2
                bot_number = "1" if winner == 1 else "2"
                winnerText = f"{winning_bot_type} (BOT {bot_number}) Won!"
            titleColor = DARK_BLUE

        width = 550
        height = 380
        x = (WIDTH - width) // 2
        y = (HEIGHT - height) // 2

        end_panel = pygame.Surface((width, height), pygame.SRCALPHA)
        end_panel.fill(panel_color)  
        pygame.draw.rect(end_panel, (255, 255, 255, 50), (0, 0, width, height), 5)
        
        title = self.subtitleFont.render(winnerText, True, titleColor)
        titleRect = title.get_rect(center=(width//2, 80))
        end_panel.blit(title, titleRect)
        
        self.screen.blit(end_panel, (x, y))

        self.playAgainButton.draw(self.screen)
        self.menuButton.draw(self.screen)

    def help_function(self):
        """Show the best move using MCTS algorithm"""
        dt = load("Game/my_tree.joblib")
        best_col = MCTSID3(3, self.game.board, 1.4142,dt)
        
        self.draw_board()
        
        # Get column center position
        center_x = best_col * SQUARE_SIZE + SQUARE_SIZE // 2
        
        # Draw an arrow or indicator above the recommended column
        arrow_color = PINK
        arrow_y = 130  # Position above the board
        
        # Draw arrow body (triangle)
        pygame.draw.polygon(self.screen, arrow_color, [(center_x, arrow_y + 40),(center_x - 20, arrow_y),(center_x + 20, arrow_y)])
        
        # Draw 'Best Move' text
        hint_font = pygame.font.Font(None, 36)
        hint_text = hint_font.render("Best Move", True, PINK)
        hint_rect = hint_text.get_rect(center=(center_x, arrow_y - 20))
        self.screen.blit(hint_text, hint_rect)
        
        pygame.display.update()
        pygame.time.wait(2000)
        
        self.state = State.GAME

    def player_move(self, game, events):
        """
        Handle player move using Pygame mouse interaction for Connect Four game.
        Returns the column (0-6) where the player wants to place their piece,
        or None if no valid move was made.
        """
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                # Get mouse position
                mouse_x, _ = pygame.mouse.get_pos()
                
                # Calculate which column was clicked
                # SQUARE_SIZE is the width of each column (180 pixels)
                column = int(mouse_x // SQUARE_SIZE)
                
                # Verify if the move is valid (0-based index)
                if game.board.verifyMove(column):
                    print("Player\nColumn: ", column+1)  
                    print("---------------------------------------------")
                    return column
        
        # Return None if no valid move was made this frame
        return None

    def get_player_func(self, player_type, player_num):
        """Get the appropriate function for the selected player type and parameters"""
        if player_type == Algorithm.HUMAN:
            return lambda game: game.player_input
        elif player_type == Algorithm.MCTS2:
            time = self.mcts_time1 if player_num == 1 else self.mcts_time2
            constant = self.mcts_constant1 if player_num == 1 else self.mcts_constant2
            return lambda state: MCTS2(time, state.board, constant)
        elif player_type == Algorithm.MCTS3:
            time = self.mcts_time1 if player_num == 1 else self.mcts_time2
            constant = self.mcts_constant1 if player_num == 1 else self.mcts_constant2
            return lambda state: MCTS3(time, state.board, constant)
        elif player_type == Algorithm.MCTSID3:
            time = self.mcts_time1 if player_num == 1 else self.mcts_time2
            constant = self.mcts_constant1 if player_num == 1 else self.mcts_constant2
            dt = load("Game/my_tree.joblib")
            return lambda state: MCTSID3(time, state.board, constant, dt)
    
    def start_game(self):        
        if self.player1_type and self.player2_type:
            player1_func = self.get_player_func(self.player1_type, 1)
            player2_func = self.get_player_func(self.player2_type, 2)

            self.game = ConnectFour(player1_func, player2_func)
            self.game.print_state()
            self.state = State.GAME
            self.input_cooldown_until = pygame.time.get_ticks() + 200
            pygame.event.clear()

    def update(self, events):
        current_time = pygame.time.get_ticks()
        if current_time >= self.input_cooldown_until:
            move = self.player_move(self.game, events)
            if move is not None:
                self.game.player_input = move
        
        self.game.simularJogo()

        if self.game.board.winner != -1:
            self.draw_board()       
            self.highlight_winner(self.game.board.col, self.game.board.row)      
            pygame.display.update()       
            pygame.time.wait(1250)
            self.state = State.END

    def reset_menu(self):
        self.state = State.MENU
        self.player1_type = None
        self.player2_type = None
        self.game = None

    def configure_algorithm(self, player):
        """Start the configuration process for the selected algorithm"""
        self.configuring_player = player
        
        default_time = self.mcts_time1 if player == 1 else self.mcts_time2
        default_const = self.mcts_constant1 if player == 1 else self.mcts_constant2
        self.mcts_time_input.text = str(default_time)
        self.mcts_constant_input.text = str(default_const)
        self.mcts_time_input.txt_surface = self.mcts_time_input.font.render(self.mcts_time_input.text, True, DARK_BLUE)
        self.mcts_constant_input.txt_surface = self.mcts_constant_input.font.render(self.mcts_constant_input.text, True, DARK_BLUE)
        self.state = State.MCTS_CONFIG

    def save_algorithm_config(self):
        """Save the configured parameters"""
        time = min(7, max(1, self.mcts_time_input.get_value() or 3))
        constant = min(7, max(1, self.mcts_constant_input.get_value() or 1.4142))
        if self.configuring_player == 1:
            self.mcts_time1 = time
            self.mcts_constant1 = constant
        else:
            self.mcts_time2 = time
            self.mcts_constant2 = constant
                
        # Return to algorithm selection screen
        self.state = State.ALGORITHM_SELECTION

    def process_events(self, events):
        """Process user input events"""
        pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT:
                return False
            
            # Process input boxes
            elif self.state == State.MCTS_CONFIG:
                self.mcts_time_input.handle_event(event)
                self.mcts_constant_input.handle_event(event)
            
            if event.type == pygame.MOUSEMOTION:
                # Update hover effect on buttons according to current state
                if self.state == State.MENU:
                    self.playButton.hover(pos)
                    self.rulesButton.hover(pos)
                elif self.state == State.ALGORITHM_SELECTION:
                    for btn in self.player1_buttons + self.player2_buttons:
                        btn.hover(pos)
                    self.backButton2.hover(pos)
                    self.startGameButton.hover(pos)
                elif self.state == State.RULES:
                    self.backButton2.hover(pos)
                elif self.state == State.END:
                    self.playAgainButton.hover(pos)
                    self.menuButton.hover(pos)
                elif self.state == State.GAME:
                    self.pauseButton.hover(pos)
                    self.helpButton.hover(pos)
                elif self.state == State.PAUSE:
                    self.resumeButton.hover(pos)
                    self.restartButton.hover(pos)
                    self.pauseMenuButton.hover(pos)
                elif self.state == State.MCTS_CONFIG:
                    self.confirmButton.hover(pos)
                    self.backButton2.hover(pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Process clicks according to current state
                if self.state == State.MENU:
                    if self.playButton.rect.collidepoint(pos):
                        self.state = State.ALGORITHM_SELECTION
                    elif self.rulesButton.rect.collidepoint(pos):
                        self.state = State.RULES
                
                elif self.state == State.ALGORITHM_SELECTION:
                    if self.humanButton1.rect.collidepoint(pos):
                        self.player1_type = Algorithm.HUMAN
                    elif self.mcts2Button1.rect.collidepoint(pos):
                        self.player1_type = Algorithm.MCTS2
                        self.configure_algorithm(1)
                    elif self.mcts3Button1.rect.collidepoint(pos):
                        self.player1_type = Algorithm.MCTS3
                        self.configure_algorithm(1)
                    elif self.mctsid3Button1.rect.collidepoint(pos):
                        self.player1_type = Algorithm.MCTSID3
                        self.configure_algorithm(1)
                    if self.humanButton2.rect.collidepoint(pos):
                        self.player2_type = Algorithm.HUMAN
                    elif self.mcts2Button2.rect.collidepoint(pos):
                        self.player2_type = Algorithm.MCTS2
                        self.configure_algorithm(2)
                    elif self.mcts3Button2.rect.collidepoint(pos):
                        self.player2_type = Algorithm.MCTS3
                        self.configure_algorithm(2)
                    elif self.mctsid3Button2.rect.collidepoint(pos):
                        self.player2_type = Algorithm.MCTSID3
                        self.configure_algorithm(2)
                    elif self.startGameButton.rect.collidepoint(pos):
                        if self.player1_type and self.player2_type:
                            self.start_game()
                    elif self.backButton2.rect.collidepoint(pos):
                        self.reset_menu()
                
                elif self.state == State.MCTS_CONFIG:
                    if self.confirmButton.rect.collidepoint(pos):
                        self.save_algorithm_config()
                    elif self.backButton2.rect.collidepoint(pos):
                        self.state = State.ALGORITHM_SELECTION
                
                elif self.state == State.RULES:
                    if self.backButton2.rect.collidepoint(pos):
                        self.reset_menu()
                
                elif self.state == State.END:
                    if self.playAgainButton.rect.collidepoint(pos):
                        self.start_game()
                    elif self.menuButton.rect.collidepoint(pos):
                        self.reset_menu()
                
                elif self.state == State.GAME:
                    if self.pauseButton.rect.collidepoint(pos):
                        self.state = State.PAUSE
                    elif self.helpButton.rect.collidepoint(pos):
                        self.state = State.HELP

                elif self.state == State.PAUSE:
                    if self.resumeButton.rect.collidepoint(pos):
                        pygame.event.clear()
                        self.input_cooldown_until = pygame.time.get_ticks() + 200
                        self.state = State.GAME
                    elif self.restartButton.rect.collidepoint(pos):
                        self.start_game()
                    elif self.pauseMenuButton.rect.collidepoint(pos):
                        self.reset_menu()
                elif self.state == State.HELP:
                    pass
        return True  # Continue the game loop

    def run(self):
        """Main game loop"""
        running = True
        while running:
            # Process events (mouse, keyboard, etc.)
            events = pygame.event.get()
            running = self.process_events(events)
            
            # Draw the current screen based on the game state
            if self.state == State.MENU:
                self.draw_menu()
            elif self.state == State.ALGORITHM_SELECTION:
                self.draw_algorithm_selection()
            elif self.state == State.RULES:
                self.draw_rules()
            elif self.state == State.MCTS_CONFIG:
                self.draw_mcts_config()
            elif self.state == State.GAME:
                self.draw_board()
                pygame.display.update()
                self.update(events)
            elif self.state == State.END:
                self.draw_end_screen()
            elif self.state == State.PAUSE:
                self.draw_pause_menu()
            elif self.state == State.HELP:
                self.help_function()    
            
            # Update display
            pygame.display.update()
            
            # Control game speed
            self.clock.tick(60)
        
        # Quit pygame when the loop ends
        pygame.quit()