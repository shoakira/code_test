import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# サンプリング点
temp_points = np.array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300])
CpR_points = np.array([1.50, 1.50, 1.51, 1.53, 1.60, 1.75, 1.95, 2.12, 2.25, 2.33, 2.38, 2.41, 2.44, 2.46, 2.48, 2.49])

# 三次スプライン補間
cs = CubicSpline(temp_points, CpR_points)

# 描画用温度範囲
temperatures = np.linspace(0, 300, 300)
CpR_smooth = cs(temperatures)

# プロット
plt.figure(figsize=(5, 4))
plt.plot(temperatures, CpR_smooth)
#plt.scatter(temp_points, CpR_points, color='red', label="Sampled Points") # サンプリング点もプロット
plt.xlabel("Temperature (K)")
plt.ylabel("C/R")
#plt.title("Reconstructed Specific Heat Curve")
plt.xlim(0, 300)
plt.ylim(1.5, 2.5)
plt.yticks([1.5, 2.0, 2.5])
plt.grid(True)
#plt.legend()

# EPSファイルとして保存
#plt.savefig('specific_heat.eps', format='eps', dpi=300, bbox_inches='tight')

plt.show()

