import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

# 図の設定 - 横長比率2:3に変更
fig, ax = plt.subplots(figsize=(9, 6))

# パラメータ設定
a = 1.0  # q²の係数
b = 2.0  # p²の係数
epsilon = 1.0  # エネルギー量子の大きさ

# 楕円を描画する関数
def draw_energy_ellipse(n, a, b, epsilon, color='blue', alpha=0.6):
    """n番目のエネルギー準位（E = n*epsilon）の楕円を描画する"""
    E = n * epsilon
    
    # 楕円の半軸長を計算
    width = 2 * np.sqrt(E / a)  # q軸方向の長さ
    height = 2 * np.sqrt(E / b)  # p軸方向の長さ
    
    # 楕円をプロット
    ellipse = Ellipse((0, 0), width, height, 
                      edgecolor=color, facecolor='none', 
                      linewidth=2, alpha=alpha, linestyle='-')
    ax.add_patch(ellipse)
    
    # エネルギー値を表示
    if n > 0:  # n=0の場合は原点のみなので表示しない
        ax.text(width/2 * 0.7, height/2 * 0.7, f'$E_{n} = {n}\\epsilon$', 
                fontsize=12, ha='center', va='center')

# 複数のエネルギー準位に対応する楕円を描画
for n in range(6):  # n=0, 1, 2, 3, 4, 5
    draw_energy_ellipse(n, a, b, epsilon, 
                        color=plt.cm.viridis(n/5), 
                        alpha=0.8-n*0.1)

# 座標軸の範囲を個別に設定
# 横軸（q軸）の範囲
q_max = 2.0  # 任意の値に変更可能
ax.set_xlim(-q_max, q_max)

# 縦軸（p軸）の範囲
p_max = 1.5  # 任意の値に変更可能
ax.set_ylim(-p_max, p_max)

# 座標軸の設定
ax.set_xlabel('$q$', fontsize=14)
ax.set_ylabel('$p$', fontsize=14)
ax.grid(True, linestyle='--', alpha=0.6)
ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)

# 縦横比を調整（'equal'のままだと、物理的な距離が等しくなる）
# 'auto'にすると、プロットエリアいっぱいに表示される
ax.set_aspect('auto')  # 'equal'から'auto'に変更


plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('energy_quantization.png', dpi=300, bbox_inches='tight')
plt.show()