def create_board():
    # 8x8のボードを初期化（空は"."、黒は"B"、白は"W"）
    board = [["." for _ in range(8)] for _ in range(8)]
    board[3][3] = "W"
    board[3][4] = "B"
    board[4][3] = "B"
    board[4][4] = "W"
    return board

def print_board(board):
    print("  " + " ".join(str(i) for i in range(8)))
    for idx, row in enumerate(board):
        print(str(idx) + " " + " ".join(row))
    print()

def is_on_board(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def get_opponent(player):
    return "B" if player == "W" else "W"

def valid_moves(board, player):
    opponent = get_opponent(player)
    moves = []
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),          (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    for x in range(8):
        for y in range(8):
            if board[x][y] != ".":
                continue
            valid = False
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if is_on_board(nx, ny) and board[nx][ny] == opponent:
                    # 1つ以上相手の石が連続しているか確認
                    nx += dx
                    ny += dy
                    while is_on_board(nx, ny) and board[nx][ny] == opponent:
                        nx += dx
                        ny += dy
                    if is_on_board(nx, ny) and board[nx][ny] == player:
                        valid = True
                        break
            if valid:
                moves.append((x, y))
    return moves

def make_move(board, player, x, y):
    opponent = get_opponent(player)
    board[x][y] = player
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),          (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    for dx, dy in directions:
        stones_to_flip = []
        nx, ny = x + dx, y + dy
        while is_on_board(nx, ny) and board[nx][ny] == opponent:
            stones_to_flip.append((nx, ny))
            nx += dx
            ny += dy
        if is_on_board(nx, ny) and board[nx][ny] == player:
            for fx, fy in stones_to_flip:
                board[fx][fy] = player
    return board

def has_any_valid_move(board, player):
    return len(valid_moves(board, player)) > 0

def game_over(board):
    # 両プレイヤー共に合法手がなければ終了
    return not (has_any_valid_move(board, "B") or has_any_valid_move(board, "W"))

def count_stones(board):
    counts = {"B": 0, "W": 0}
    for row in board:
        for cell in row:
            if cell in counts:
                counts[cell] += 1
    return counts

def main():
    board = create_board()
    current_player = "B"  # 黒から開始
    while not game_over(board):
        print_board(board)
        moves = valid_moves(board, current_player)
        if moves:
            print(f"{current_player}の手番です。合法手: {moves}")
            try:
                move_input = input("行,列の形式で入力 (例: 2,3): ")
                if move_input.lower() in ["q", "quit", "exit"]:
                    print("ゲーム中断")
                    return
                x_str, y_str = move_input.split(",")
                move = (int(x_str.strip()), int(y_str.strip()))
            except Exception as e:
                print("入力形式が正しくありません。再入力してください。")
                continue
            if move in moves:
                board = make_move(board, current_player, move[0], move[1])
            else:
                print("不正な手です。再度入力してください。")
                continue
        else:
            print(f"{current_player}は打てる手がありません。パスします。")
        current_player = get_opponent(current_player)
    
    print_board(board)
    counts = count_stones(board)
    print("ゲーム終了!")
    print("結果:", counts)
    if counts["B"] > counts["W"]:
        print("黒の勝利!")
    elif counts["W"] > counts["B"]:
        print("白の勝利!")
    else:
        print("引き分けです。")

if __name__ == "__main__":
    main()