import matplotlib.pyplot as plt
import numpy as np

# --- 質量と座標の定義 ---
M1 = 1.0
M2 = 1.0
O  = np.array([0.0, 0.0])       # 原点
m1 = np.array([-0.6, 0.8])       # 質点 m1 の位置
m2 = np.array([0.8, 0.6])        # 質点 m2 の位置

# 重心 G の計算: G = (M1*m1 + M2*m2)/(M1+M2)
G = (M1*m1 + M2*m2) / (M1 + M2)

# --- 描画設定 ---
fig, ax = plt.subplots(figsize=(6, 6))

# 質点と重心のプロット
ax.scatter(O[0], O[1], color='black', s=50, zorder=5)
ax.scatter(m1[0], m1[1], color='black', s=50, zorder=5)
ax.scatter(m2[0], m2[1], color='black', s=50, zorder=5)
ax.scatter(G[0], G[1], color='green', s=70, zorder=5)

# 原点から各質点への位置ベクトル（黒い矢印）を描画
ax.quiver(O[0], O[1], m1[0], m1[1],
          angles='xy', scale_units='xy', scale=1,
          color='black', width=0.005, label=r'$\mathbf{r}_1$')
ax.quiver(O[0], O[1], m2[0], m2[1],
          angles='xy', scale_units='xy', scale=1,
          color='black', width=0.005, label=r'$\mathbf{r}_2$')

# 原点から重心 G へのベクトル（緑の矢印）
ax.quiver(O[0], O[1], G[0], G[1],
          angles='xy', scale_units='xy', scale=1,
          color='green', width=0.005, label=r'$\mathbf{r}_G$')

# 重心から各質点への相対ベクトル（赤の破線矢印）
ax.annotate("",
            xy=m1, xytext=G,
            arrowprops=dict(arrowstyle="->", color="red",
                            linestyle='dashed', linewidth=1.5))
ax.annotate("",
            xy=m2, xytext=G,
            arrowprops=dict(arrowstyle="->", color="red",
                            linestyle='dashed', linewidth=1.5))

# 各点のラベル
ax.text(O[0]-0.05, O[1]-0.05, "O", fontsize=12, ha='right')
ax.text(m1[0]-0.05, m1[1]+0.05, r"$m_1$", fontsize=12, ha='right')
ax.text(m2[0]+0.05, m2[1]+0.05, r"$m_2$", fontsize=12, ha='left')
ax.text(G[0], G[1]-0.1, r"$G$", fontsize=12, ha='center', color='green')

# 軸設定と装飾
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-0.2, 1.2)
ax.set_aspect('equal', 'box')
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_title("Two-Body System with Center of Mass")
ax.grid(True)
ax.legend(loc='upper left')

plt.show()
