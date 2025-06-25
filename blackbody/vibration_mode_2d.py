import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# 図のサイズを設定
plt.figure(figsize=(7, 7))

# 軸ラベル
plt.xlabel('x', fontsize=14)
plt.ylabel('y', fontsize=14)

# 軸の範囲
plt.xlim(0, 5)
plt.ylim(5, 0)  # 上下反転してyが下向きになるように

# 軸の矢印
plt.annotate("", xy=(5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="->", linewidth=1.5))
plt.annotate("", xy=(0, 5), xytext=(0, 0), arrowprops=dict(arrowstyle="->", linewidth=1.5))

# サブプロットのサイズと間隔
box_size = 0.8
margin = 0.2
modes = 4  # 4x4のグリッド

# 各モードを描画
for i in range(modes):  # y方向のモード(行)
    for j in range(modes):  # x方向のモード(列)
        # ボックスの位置を計算
        x_pos = j * (box_size + margin) + 0.5
        y_pos = i * (box_size + margin) + 0.5
        
        # 外枠の矩形を描画
        rect = Rectangle((x_pos, y_pos), box_size, box_size, fill=False, edgecolor='black', linewidth=1.5)
        plt.gca().add_patch(rect)
        
        # 最上段（i=0）: 水平線のみ（等間隔）
        if i == 0:
            # j個の区画に分割（j+1等分）
            for h in range(1, j+1):
                y_line = y_pos + h * (box_size / (j+1))
                plt.plot([x_pos, x_pos + box_size], [y_line, y_line], 'k-', linewidth=1.5)
        
        # 左端の列（j=0）: 垂直線のみ
        elif j == 0:
            # i個の区画に分割（i+1等分）
            for v in range(1, i+1):
                x_line = x_pos + v * (box_size / (i+1))
                plt.plot([x_line, x_line], [y_pos, y_pos + box_size], 'k-', linewidth=1.5)
        
        # その他のセル: 水平・垂直の分割の組み合わせ
        else:
            # 水平線（j+1等分）
            for h in range(1, j+1):
                y_line = y_pos + h * (box_size / (j+1))
                plt.plot([x_pos, x_pos + box_size], [y_line, y_line], 'k-', linewidth=1.5)
            
            # 垂直線（i+1等分）
            for v in range(1, i+1):
                x_line = x_pos + v * (box_size / (i+1))
                plt.plot([x_line, x_line], [y_pos, y_pos + box_size], 'k-', linewidth=1.5)

# 余分な目盛りとフレームを削除
plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
plt.box(False)

# 保存と表示
plt.tight_layout()
plt.savefig('rectangular_vibration_modes.png', dpi=300)
plt.show()