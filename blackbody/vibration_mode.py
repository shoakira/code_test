import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

# フィギュアの設定
fig, ax = plt.subplots(4, 1, figsize=(5, 4))
plt.subplots_adjust(hspace=0.4)

# 共通パラメータ
length = 10  # 弦の長さ
amplitude = 1.0  # 振幅

# 1. 基本振動モード（1次）
x1 = np.linspace(0, length, 1000)
y1_top = amplitude * np.sin(np.pi * x1 / length)
y1_bottom = -y1_top
ax[0].plot(x1, y1_top, 'k-', linewidth=2)
ax[0].plot(x1, y1_bottom, 'k-', linewidth=2)
ax[0].plot([0, length], [0, 0], 'k-', linewidth=1)

# 2. 2次振動モード
x2 = np.linspace(0, length, 1000)
y2_top = amplitude * np.sin(2 * np.pi * x2 / length)
y2_bottom = -y2_top
ax[1].plot(x2, y2_top, 'k-', linewidth=2)
ax[1].plot(x2, y2_bottom, 'k-', linewidth=2)
ax[1].plot([0, length], [0, 0], 'k-', linewidth=1)

# 3. 3次振動モード
x3 = np.linspace(0, length, 1000)
y3_top = amplitude * np.sin(3 * np.pi * x3 / length)
y3_bottom = -y3_top
ax[2].plot(x3, y3_top, 'k-', linewidth=2)
ax[2].plot(x3, y3_bottom, 'k-', linewidth=2)
ax[2].plot([0, length], [0, 0], 'k-', linewidth=1)

# 4. 4次振動モード
x4 = np.linspace(0, length, 1000)
y4_top = amplitude * np.sin(4 * np.pi * x4 / length)
y4_bottom = -y4_top
ax[3].plot(x4, y4_top, 'k-', linewidth=2)
ax[3].plot(x4, y4_bottom, 'k-', linewidth=2)
ax[3].plot([0, length], [0, 0], 'k-', linewidth=1)



# 各サブプロットの設定
for a in ax:
    a.set_xlim(0, length)
    a.set_ylim(-1.2, 1.2)
    a.axis('off')  # 軸を非表示

plt.tight_layout()
plt.savefig('string_vibration_modes.png', dpi=300)
plt.show()