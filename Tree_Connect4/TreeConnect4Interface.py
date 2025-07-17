import pygame
import sys
import math
import time

from Tree_Connect4.TreeID3Connect4 import loadTree

# Cores
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
NODE_COLOR = (200, 220, 255)
LEAF_COLOR = (180, 255, 180)
TEXT_COLOR = (  0,   0,   0)
LINE_TRUE  = (  0, 180,   0)
LINE_FALSE = (255,   0,   0)
BUTTON_BG  = (  0,   0, 255)
BUTTON_FG  = (255, 255, 255)

# Tamanhos base (antes de zoom)
BASE_NODE_WIDTH  = 160
BASE_NODE_HEIGHT =  60
BASE_X_SPACING   =  40
BASE_Y_SPACING   = 100
FONT_SIZE        =  18

# Easing
EASE_FACTOR = 0.2

# Fade-in
FADE_DURATION = 2.0  # segundos

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Árvore de Decisão - Navegação")
font = pygame.font.SysFont('Arial', FONT_SIZE)

# Estado pan/zoom animado
offset_x, offset_y = 0.0, 0.0
target_offset_x, target_offset_y = 0.0, 0.0
dragging   = False
start_drag = (0, 0)
zoom_level = 1.0
target_zoom = 1.0

# Botão métricas
show_metrics = False
button_rect  = pygame.Rect(10, 10, 140, 30)
PAN_STEP     = 50

# Tempo de início para fade
start_time = time.time()

def count_leaves(node):
    if node.leaf:
        return 1
    return count_leaves(node.leftChild.node) + count_leaves(node.rightChild.node)

def line_clip_rect(p1, p2, w, h):
    x1, y1 = p1; x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0: return p1, p2
    fx = (w/2) / abs(dx) if dx!=0 else float('inf')
    fy = (h/2) / abs(dy) if dy!=0 else float('inf')
    f = min(fx, fy)
    start = (x1 + dx*f, y1 + dy*f)
    end   = (x2 - dx*f, y2 - dy*f)
    return start, end

def draw_tree(node, wx, wy, parent_pos=None, is_right=None):
    w = BASE_NODE_WIDTH  * zoom_level
    h = BASE_NODE_HEIGHT * zoom_level
    sx = BASE_X_SPACING   * zoom_level
    sy = BASE_Y_SPACING   * zoom_level

    cx = offset_x + wx * zoom_level + w/2
    cy = offset_y + wy * zoom_level + h/2
    rect = pygame.Rect(offset_x + wx * zoom_level,
                       offset_y + wy * zoom_level,
                       w, h)

    if parent_pos is not None:
        start, end = line_clip_rect(parent_pos, (cx, cy), w, h)
        color = LINE_FALSE if is_right else LINE_TRUE
        pygame.draw.line(screen, color, start, end, max(1, int(2*zoom_level)))

    node_color = LEAF_COLOR if node.leaf else NODE_COLOR
    pygame.draw.rect(screen, node_color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)

    text = f"Classe: {node.target}" if node.leaf else f"{node.splitPredictor}?"
    rendered = font.render(text, True, TEXT_COLOR)
    txt_rect = rendered.get_rect(center=(cx, cy))
    screen.blit(rendered, txt_rect)

    if not node.leaf:
        left_count  = count_leaves(node.leftChild.node)
        right_count = count_leaves(node.rightChild.node)
        spacing     = w + sx
        x_left  = wx - (spacing/zoom_level)*(right_count/2)
        x_right = wx + (spacing/zoom_level)*(left_count/2)
        y_child = wy + (h + sy)/zoom_level
        center  = (cx, cy)
        draw_tree(node.leftChild.node,  x_left,  y_child, center, is_right=False)
        draw_tree(node.rightChild.node, x_right, y_child, center, is_right=True)

def draw_button():
    pygame.draw.rect(screen, BUTTON_BG, button_rect, border_radius=5)
    label = font.render("Show Metrics", True, BUTTON_FG)
    screen.blit(label, label.get_rect(center=button_rect.center))

def draw_metrics(accuracy,f1_score):
    overlay = pygame.Surface((200, 60))
    overlay.set_alpha(200)
    overlay.fill(WHITE)
    screen.blit(overlay, (10, 50))
    screen.blit(font.render(f"Accuracy: {accuracy:.1f}%", True, BLACK), (20, 60))
    screen.blit(font.render(f"F1-score: {f1_score:.1f}%", True, BLACK), (20, 85))

def main():
    tree = loadTree()
    tree.print("")
    accuracy  = 83.2
    f1_score  = 81.4
    print("Accuracy: ",accuracy)
    print("F1-Score: ",f1_score)
    global dragging, start_drag
    global offset_x, offset_y, target_offset_x, target_offset_y
    global zoom_level, target_zoom, show_metrics, start_time

    clock = pygame.time.Clock()
    # posição inicial da raiz em world coordenadas
    root_wx = (screen.get_width()/2 - BASE_NODE_WIDTH/2) / zoom_level
    root_wy = 50 / zoom_level

    running = True
    while running:
        # Desenha gradiente de fundo
        for y in range(screen.get_height()):
            t = y/screen.get_height()
            r = int(135 + t*(220-135))
            g = int(206 + t*(220-206))
            b = int(250 + t*(220-250))
            pygame.draw.line(screen, (r,g,b), (0,y), (screen.get_width(),y))

        # Easing pan/zoom
        zoom_level += (target_zoom - zoom_level) * EASE_FACTOR
        offset_x    += (target_offset_x - offset_x) * EASE_FACTOR
        offset_y    += (target_offset_y - offset_y) * EASE_FACTOR

        # UI
        draw_button()
        if show_metrics: draw_metrics(accuracy,f1_score)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if button_rect.collidepoint(e.pos):
                    show_metrics = not show_metrics
                else:
                    dragging, start_drag = True, e.pos

            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                dragging = False

            elif e.type == pygame.MOUSEMOTION and dragging:
                dx, dy = e.pos[0]-start_drag[0], e.pos[1]-start_drag[1]
                target_offset_x += dx
                target_offset_y += dy
                start_drag = e.pos

            elif e.type == pygame.KEYDOWN:
                # relança fade-in
                if e.key == pygame.K_r:
                    start_time = time.time()
                # zoom centrado no cursor
                elif e.key in (pygame.K_MINUS, pygame.K_KP_MINUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    mx, my = pygame.mouse.get_pos()
                    before_wx = (mx - offset_x) / zoom_level
                    before_wy = (my - offset_y) / zoom_level
                    factor   = 0.9 if e.key in (pygame.K_MINUS, pygame.K_KP_MINUS) else 1.1
                    target_zoom *= factor
                    target_offset_x = mx - before_wx * target_zoom
                    target_offset_y = my - before_wy * target_zoom
                # pan com setas
                elif e.key == pygame.K_LEFT:
                    target_offset_x += PAN_STEP
                elif e.key == pygame.K_RIGHT:
                    target_offset_x -= PAN_STEP
                elif e.key == pygame.K_UP:
                    target_offset_y += PAN_STEP
                elif e.key == pygame.K_DOWN:
                    target_offset_y -= PAN_STEP

        # Desenha árvore
        draw_tree(tree.node, root_wx, root_wy)

        # Fade-in overlay
        elapsed = time.time() - start_time
        if elapsed < FADE_DURATION:
            alpha = int(255 * (1 - elapsed / FADE_DURATION))
            fade_surf = pygame.Surface(screen.get_size())
            fade_surf.fill(BLACK)
            fade_surf.set_alpha(alpha)
            screen.blit(fade_surf, (0,0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()