from enum import Enum

class State(Enum):
    MENU = 1
    GAME = 2
    END = 3
    RULES = 4
    ALGORITHM_SELECTION = 5
    PAUSE = 6
    MINMAX_CONFIG = 7  
    MCTS_CONFIG = 8   
    HELP = 9 

class Algorithm(Enum):
    HUMAN = 1
    MCTS2 = 2
    MCTS3 = 3
    MCTSID3 = 4

    def __str__(self):
        names = {
            Algorithm.MCTS2: "MCTS2",
            Algorithm.MCTS3: "MCTS3",
            Algorithm.MCTSID3: "MCTSID3",
            Algorithm.HUMAN: "Human"
        }
        return names.get(self)
    