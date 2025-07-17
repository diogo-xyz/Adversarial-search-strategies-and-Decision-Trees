import pygame
from Game.Constants import *

class Button:
    def __init__(self, x, y, width, height, text, normalColor, hoverColor):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.normalColor = normalColor
        self.hoverColor = hoverColor
        self.currentColor = normalColor
        self.font = pygame.font.Font(None, 42)

    def draw(self, screen):
        pygame.draw.rect(screen, self.currentColor, self.rect)
        textSurface = self.font.render(self.text, True, DARK_BLUE)
        textRect = textSurface.get_rect(center=self.rect.center)
        screen.blit(textSurface, textRect)

    def hover(self, pos):
        self.currentColor = self.hoverColor if self.rect.collidepoint(pos) else self.normalColor

class InputBox:
    def __init__(self, x, y, w, h, default_text='', text_limit=6, numeric_only=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color(LIGHT_CYAN)
        self.color_active = pygame.Color(YELLOW)
        self.color = self.color_inactive
        self.text = default_text
        self.font = pygame.font.Font(None, 70)
        self.txt_surface = self.font.render(self.text, True, DARK_BLUE)
        self.active = False
        self.text_limit = text_limit
        self.numeric_only = numeric_only

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    new_char = event.unicode
                    if self.numeric_only and not (new_char.isdigit() or (new_char == '.' and '.' not in self.text)):
                        return None
                    if len(self.text) < self.text_limit:
                        self.text += new_char
                self.txt_surface = self.font.render(self.text, True, DARK_BLUE)
        return None

    def draw(self, screen):
        text_width = self.txt_surface.get_width()
        text_height = self.txt_surface.get_height()
        text_x = self.rect.x + (self.rect.width - text_width) // 2
        text_y = self.rect.y + (self.rect.height - text_height) // 2
        
        screen.blit(self.txt_surface, (text_x, text_y))
        
        pygame.draw.rect(screen, self.color, self.rect, 2)
    
    def get_value(self):
        try:
            if self.text:
                return float(self.text)
            return 0
        except ValueError:
            return 0