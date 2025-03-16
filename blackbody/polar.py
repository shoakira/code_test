import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches

# 図のセットアップ
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# 軸の範囲を設定
ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([-2, 2])

# 座標軸のラベル
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# 原点O
ax.text(0.1, 0.1, 0.1, 'O', fontsize=14)

# 座標軸の描画
ax.quiver(0, 0, 0, 3, 0, 0, color='k', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0, 0, 3, 0, color='k', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0, 0, 0, 3, color='k', arrow_length_ratio=0.1)

# 点を3次元空間に配置
# 極角θと方位角φを定義
r = 1.5  # 半径
theta = np.pi/4  # z軸からの角度
phi = np.pi/4    # xy平面上での角度

# 球座標から直交座標への変換
x = r * np.sin(theta) * np.cos(phi)
y = r * np.sin(theta) * np.sin(phi)
z = r * np.cos(theta)

# 点の描画
ax.scatter([0], [0], [0], color='k', s=50)  # 原点
ax.scatter([x], [y], [z], color='k', s=50)  # 球座標上の点

# θ角度の弧を描画（z軸からの角度）
u = np.linspace(0, theta, 30)
x_theta = 0.5 * np.sin(u)
y_theta = 0
z_theta = 0.5 * np.cos(u)
ax.plot(x_theta, y_theta, z_theta, 'k-')
ax.text(0.3, 0, 0.5, r'$\theta$', fontsize=14)

# θ方向を示す矢印
u_mid = theta / 2
x_arrow = 0.5 * np.sin(u_mid)
z_arrow = 0.5 * np.cos(u_mid)
ax.quiver(x_arrow, 0, z_arrow, np.cos(u_mid), 0, -np.sin(u_mid), 
          color='k', length=0.2, arrow_length_ratio=0.3)

# φ角度の弧を描画（xy平面上の角度）
v = np.linspace(0, phi, 30)
x_phi = 0.5 * np.cos(v)
y_phi = 0.5 * np.sin(v)
z_phi = 0
ax.plot(x_phi, y_phi, z_phi, 'k-')
ax.text(0.4, 0.2, 0, r'$\phi$', fontsize=14)

# φ方向を示す矢印
v_mid = phi / 2
x_arr_phi = 0.5 * np.cos(v_mid)
y_arr_phi = 0.5 * np.sin(v_mid)
ax.quiver(x_arr_phi, y_arr_phi, 0, -np.sin(v_mid), np.cos(v_mid), 0, 
          color='k', length=0.2, arrow_length_ratio=0.3)

# 点と原点を結ぶ線
ax.plot([0, x], [0, y], [0, z], 'k--', alpha=0.5)

# 点から軸への射影（ガイドライン）
ax.plot([x, x], [y, y], [0, z], 'k:', alpha=0.5)
ax.plot([x, 0], [y, 0], [0, 0], 'k:', alpha=0.5)

# グリッドをオフにする
ax.grid(False)

# 軸のスケールを等しくする
ax.set_box_aspect([1, 1, 1])

# 余分な目盛りを削除
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])

# 余分な枠線を削除
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.xaxis.pane.set_edgecolor('w')
ax.yaxis.pane.set_edgecolor('w')
ax.zaxis.pane.set_edgecolor('w')

# ビュー角度を調整（添付図と同様の視点に）
ax.view_init(elev=20, azim=-45)

plt.tight_layout()
plt.savefig('spherical_coordinates.png', dpi=300)
plt.show()