import pygame
import sys
import time
from Iris.TreeID3 import mainID3

# ============ CONFIG ===============
WINDOW_WIDTH, WINDOW_HEIGHT = 1400, 900
INPUT_AREA_HEIGHT   = 250
# ===================================


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Árvore de Decisão - Iris")

    # Cores básicas
    WHITE = (255, 255, 255)
    BLACK = (  0,   0,   0)

    FONT     = pygame.font.SysFont("Arial", 20)
    BIG_FONT = pygame.font.SysFont("Arial", 26)
    clock    = pygame.time.Clock()

    # Carrega e treina árvore
    tree,accuracy,f1score,auc = mainID3()

    # Estado de input
    input_fields = {"sepallength":"","sepalwidth":"","petallength":"","petalwidth":""}
    active_field      = None
    prediction_result = ""
    prediction_probs  = {}

    # Pan & Zoom
    offset_x, offset_y = 0.0, 0.0
    zoom_level         = 1.0

    # Drag com rato
    dragging       = False
    last_mouse_pos = (0, 0)

    # Avaliar o modelo
    print("Accuracy: ",accuracy)
    print("F1-Score: ",f1score)
    print("AUC: ",auc)


    # Mostrar métricas?
    show_metrics = False

    # Botões
    metrics_btn_rect = pygame.Rect(50+100+180, WINDOW_HEIGHT-60, 180, 40)
    predict_btn_rect = pygame.Rect(50+100, WINDOW_HEIGHT-60, 150, 40)

    # Fade-in
    FADE_DURATION = 2.0
    start_time    = time.time()

    # Nó base antes do zoom
    NODE_W, NODE_H = 200, 40

    def draw_text(text, x, y, color=BLACK, font=FONT):
        surf = font.render(text, True, color)
        screen.blit(surf, (x, y))

    def draw_node(node, world_x, world_y, base_spacing, depth=0):
        if node is None: return

        # escala tamanhos
        w = NODE_W * zoom_level
        h = NODE_H * zoom_level
        # converte world -> screen
        sx = offset_x + world_x * zoom_level
        sy = offset_y + world_y * zoom_level

        # retângulo do nó
        rect = pygame.Rect(sx - w/2, sy, w, h)
        pygame.draw.rect(screen, (200,230,255), rect, border_radius=int(5*zoom_level))
        pygame.draw.rect(screen, BLACK, rect, max(1,int(2*zoom_level)), border_radius=int(5*zoom_level))

        # label
        if node.leaf:
            label = f"Leaf: {node.target}"
        else:
            label = f"{node.splitPredictor} < {getattr(node,'split',0):.2f}"
        draw_text(label,
                sx - w/2 + 10*zoom_level,
                sy + 10*zoom_level,
                font=pygame.font.SysFont("Arial", int(20*zoom_level)))

        # centrobaixo do nó
        cx, cy = sx, sy + h

        # filhos
        raw_spacing = base_spacing / (2**depth)
        child_dy = 160/zoom_level
        if node.leftChild:
            wx = world_x - raw_spacing
            wy = world_y + child_dy
            tx = offset_x + wx*zoom_level
            ty = offset_y + wy*zoom_level
            pygame.draw.line(screen, (0,180,0), (cx,cy), (tx,ty), max(1,int(2*zoom_level)))
            draw_node(node.leftChild.node, wx, wy, base_spacing, depth+1)
        if node.rightChild:
            wx = world_x + raw_spacing
            wy = world_y + child_dy
            tx = offset_x + wx*zoom_level
            ty = offset_y + wy*zoom_level
            pygame.draw.line(screen, (255,0,0), (cx,cy), (tx,ty), max(1,int(2*zoom_level)))
            draw_node(node.rightChild.node, wx, wy, base_spacing, depth+1)

    while True:
        # Fundo: gradiente vertical
        for yy in range(WINDOW_HEIGHT):
            t = yy / WINDOW_HEIGHT
            r = int(135 + t*(220-135))
            g = int(206 + t*(220-206))
            b = int(250 + t*(220-250))
            pygame.draw.line(screen, (r,g,b), (0,yy), (WINDOW_WIDTH,yy))

        # Desenha árvore
        root_wx = (WINDOW_WIDTH/2) / zoom_level
        root_wy = 20  / zoom_level
        draw_node(tree.node, root_wx, root_wy, base_spacing=700)

        # Eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # drag com rato e clique em botões
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if metrics_btn_rect.collidepoint(e.pos):
                    show_metrics = not show_metrics
                elif predict_btn_rect.collidepoint(e.pos):
                    # executar previsão
                    if all(v.strip() for v in input_fields.values()):
                        sample = {k: float(v) for k,v in input_fields.items()}
                        sample["class"] = ""
                        try:
                            prediction_result, prediction_probs = tree.predict(sample)
                        except:
                            prediction_result, prediction_probs = "Erro", {}
                    else:
                        prediction_result, prediction_probs = "Preencha todos os campos.", {}
                else:
                    dragging = True
                    last_mouse_pos = e.pos
                    # ativa campo de texto?
                    inp_y = WINDOW_HEIGHT - INPUT_AREA_HEIGHT
                    for i, key in enumerate(input_fields):
                        ix, iy = 50+100, inp_y + i*40
                        if ix <= e.pos[0] <= ix+140 and iy <= e.pos[1] <= iy+30:
                            active_field = key

            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                dragging = False

            elif e.type == pygame.MOUSEMOTION and dragging:
                dx, dy     = e.pos[0] - last_mouse_pos[0], e.pos[1] - last_mouse_pos[1]
                offset_x  += dx
                offset_y  += dy
                last_mouse_pos = e.pos

            elif e.type == pygame.KEYDOWN:
                # relança fade-in
                if e.key == pygame.K_r:
                    start_time = time.time()
                # pan por setas
                elif e.key == pygame.K_LEFT:
                    offset_x += 50
                elif e.key == pygame.K_RIGHT:
                    offset_x -= 50
                elif e.key == pygame.K_UP:
                    offset_y += 50
                elif e.key == pygame.K_DOWN:
                    offset_y -= 50
                # zoom
                elif e.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    zoom_level = max(0.1, zoom_level * 0.9)
                elif e.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    zoom_level *= 1.1
                # inputs de texto
                if active_field:
                    if e.key == pygame.K_BACKSPACE:
                        input_fields[active_field] = input_fields[active_field][:-1]
                    elif e.unicode in '0123456789.-':
                        input_fields[active_field] += e.unicode
                # Enter também pode prever
                if e.key == pygame.K_RETURN:
                    if all(v.strip() for v in input_fields.values()):
                        sample = {k: float(v) for k,v in input_fields.items()}
                        sample["class"] = ""
                        try:
                            prediction_result, prediction_probs = tree.predict(sample)
                        except:
                            prediction_result, prediction_probs = "Erro", {}
                    else:
                        prediction_result, prediction_probs = "Preencha todos os campos.", {}

        # Inputs
        inp_y = WINDOW_HEIGHT - INPUT_AREA_HEIGHT
        for i,(k,v) in enumerate(input_fields.items()):
            ix, iy = 50+100, inp_y + i*40
            pygame.draw.rect(screen, (230,230,230), (ix,iy,140,30))
            border_col = (0,120,255) if active_field==k else BLACK
            pygame.draw.rect(screen, border_col, (ix,iy,140,30), 2)
            draw_text(f"{k}:", 50, iy+5)
            draw_text(v, ix+5, iy+5)

        # Botões
        pygame.draw.rect(screen, (0,200,0), predict_btn_rect)
        draw_text("Prever", predict_btn_rect.x+40, predict_btn_rect.y+10, color=WHITE)
        pygame.draw.rect(screen, (0,100,200), metrics_btn_rect)
        draw_text(("HIDE" if show_metrics else "SHOW") + " METRICS",
                metrics_btn_rect.x+15, metrics_btn_rect.y+10, color=WHITE)

        # Métricas
        if show_metrics:
            draw_text("Model's Metrics:", 50, inp_y-100, font=BIG_FONT)
            draw_text(f"Accuracy: {accuracy:.3f}", 50, inp_y-70)
            draw_text(f"F1 Score:  {f1score:.3f}", 50, inp_y-50)
            draw_text(f"ROC-AUC:   {auc:.3f}",  50, inp_y-30)

        # Resultado
        if prediction_result:
            draw_text(f"Resultado: {prediction_result}", predict_btn_rect.x+180, predict_btn_rect.y-150,
                    font=BIG_FONT, color=(0,100,0))
            if prediction_probs:
                draw_text("Probabilidades:", predict_btn_rect.x+180, predict_btn_rect.y-120)
                for i,(cls,p) in enumerate(prediction_probs.items()):
                    draw_text(f"- {cls}: {p:.2f}",
                            predict_btn_rect.x+180, predict_btn_rect.y-100+i*20)

        # Fade-in overlay
        elapsed = time.time() - start_time
        if elapsed < FADE_DURATION:
            alpha = int(255 * (1 - elapsed/FADE_DURATION))
            fade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade.fill(BLACK)
            fade.set_alpha(alpha)
            screen.blit(fade, (0,0))

        pygame.display.flip()
        clock.tick(60)