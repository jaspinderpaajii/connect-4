import math
import pygame

ROWS, COLS = 6, 7
CELL = 90
TOP = 100
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + TOP
EMPTY, HUMAN, AI = 0, 1, 2
DEPTH = 5
BLUE = (35, 91, 185)
DARK = (19, 29, 49)
WHITE = (244, 247, 251)
RED = (235, 73, 81)
YELLOW = (250, 206, 61)
GREY = (194, 203, 218)


def valid_columns(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY]


def drop_piece(board, col, piece):
    result = [row[:] for row in board]
    for row in range(ROWS - 1, -1, -1):
        if result[row][col] == EMPTY:
            result[row][col] = piece
            return result
    return None


def winning_move(board, piece):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != piece:
                continue
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                if all(0 <= r + dr*i < ROWS and 0 <= c + dc*i < COLS
                       and board[r + dr*i][c + dc*i] == piece for i in range(4)):
                    return True
    return False


def score_window(window):
    ai = window.count(AI)
    human = window.count(HUMAN)
    empty = window.count(EMPTY)
    if ai and human:
        return 0
    if ai == 4:
        return 100000
    if human == 4:
        return -100000
    if ai == 3 and empty == 1:
        return 100
    if ai == 2 and empty == 2:
        return 10
    if human == 3 and empty == 1:
        return -120
    if human == 2 and empty == 2:
        return -12
    return 0


def evaluate(board):
    score = sum(row[COLS // 2] == AI for row in board) * 6
    score -= sum(row[COLS // 2] == HUMAN for row in board) * 6
    windows = []
    for r in range(ROWS):
        for c in range(COLS - 3):
            windows.append([board[r][c + i] for i in range(4)])
    for r in range(ROWS - 3):
        for c in range(COLS):
            windows.append([board[r + i][c] for i in range(4)])
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            windows.append([board[r + i][c + i] for i in range(4)])
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            windows.append([board[r + i][c - i] for i in range(4)])
    return score + sum(score_window(w) for w in windows)


def minimax(board, depth, alpha, beta, maximizing, stats):
    stats['nodes'] += 1
    valid = valid_columns(board)
    if winning_move(board, AI):
        return None, 1000000 + depth
    if winning_move(board, HUMAN):
        return None, -1000000 - depth
    if not valid:
        return None, 0
    if depth == 0:
        return None, evaluate(board)

    # Prefer central columns when scores are equal.
    valid.sort(key=lambda c: abs(c - COLS // 2))
    best_col = valid[0]
    if maximizing:
        best = -math.inf
        for index, col in enumerate(valid):
            child = drop_piece(board, col, AI)
            _, value = minimax(child, depth - 1, alpha, beta, False, stats)
            if value > best:
                best, best_col = value, col
            alpha = max(alpha, best)
            if alpha >= beta:
                stats['cutoffs'] += 1
                break
        return best_col, best
    else:
        best = math.inf
        for index, col in enumerate(valid):
            child = drop_piece(board, col, HUMAN)
            _, value = minimax(child, depth - 1, alpha, beta, True, stats)
            if value < best:
                best, best_col = value, col
            beta = min(beta, best)
            if alpha >= beta:
                stats['cutoffs'] += 1
                break
        return best_col, best


def draw(screen, board, font, small, message, stats):
    screen.fill(DARK)
    heading = font.render(message, True, WHITE)
    screen.blit(heading, (18, 12))
    info = small.render(
        f"You: RED   AI: YELLOW   Depth: {DEPTH}   Nodes: {stats['nodes']}   Cutoffs: {stats['cutoffs']}",
        True, GREY
    )
    screen.blit(info, (18, 52))
    tip = small.render("Click a column to drop a disc  |  Press R to restart  |  ESC to quit", True, GREY)
    screen.blit(tip, (18, 76))
    pygame.draw.rect(screen, BLUE, (0, TOP, WIDTH, ROWS * CELL))
    for r in range(ROWS):
        for c in range(COLS):
            color = (31, 43, 67) if board[r][c] == EMPTY else RED if board[r][c] == HUMAN else YELLOW
            pygame.draw.circle(screen, color, (c * CELL + CELL // 2, TOP + r * CELL + CELL // 2), CELL // 2 - 8)
    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect Four | Minimax + Alpha-Beta Pruning")
    font = pygame.font.SysFont("arial", 26, bold=True)
    small = pygame.font.SysFont("arial", 15)
    clock = pygame.time.Clock()
    board = [[EMPTY] * COLS for _ in range(ROWS)]
    stats = {'nodes': 0, 'cutoffs': 0}
    message, game_over = "Your turn!", False
    print("Connect Four | Human vs Minimax AI | Alpha-Beta Pruning")
    print("You play RED (1); AI plays YELLOW (2).")

    running = True
    while running:
        draw(screen, board, font, small, message, stats)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    board = [[EMPTY] * COLS for _ in range(ROWS)]
                    stats = {'nodes': 0, 'cutoffs': 0}
                    message, game_over = "Your turn!", False
                    print("Game restarted")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                mx, my = event.pos
                if my < TOP:
                    continue
                col = mx // CELL
                if col not in valid_columns(board):
                    continue
                board = drop_piece(board, col, HUMAN)
                print(f"Human played column {col + 1}")
                if winning_move(board, HUMAN):
                    message, game_over = "You win! Press R to restart.", True
                elif not valid_columns(board):
                    message, game_over = "Draw! Press R to restart.", True
                else:
                    message = "AI is thinking..."
                    draw(screen, board, font, small, message, stats)
                    pygame.event.pump()
                    stats = {'nodes': 0, 'cutoffs': 0}
                    ai_col, value = minimax(board, DEPTH, -math.inf, math.inf, True, stats)
                    board = drop_piece(board, ai_col, AI)
                    print(f"AI played column {ai_col + 1} | score={value} | "
                          f"nodes={stats['nodes']} | cutoffs={stats['cutoffs']}")
                    if winning_move(board, AI):
                        message, game_over = "AI wins! Press R to restart.", True
                    elif not valid_columns(board):
                        message, game_over = "Draw! Press R to restart.", True
                    else:
                        message = "Your turn!"
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
