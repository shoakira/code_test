import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# フィッティング関数の定義
# この関数は(0,0)を通り、xが大きくなると上限値aに漸近する
def fitting_function(x, a, b, c):
    return a * (1 - np.exp(-b * x**c))

# グラフから読み取ったデータポイント
temperatures = np.array([0, 2, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100])
specific_heats = np.array([0, 0.05, 0.2, 0.52, 0.95, 1.45, 1.9, 2.25, 2.5, 2.7, 2.85, 2.92, 2.96, 2.98, 2.99, 3.0])

# パラメータの初期値
initial_params = [3.0, 0.01, 1.5]

# フィッティング実行
params, _ = curve_fit(fitting_function, temperatures, specific_heats, p0=initial_params)

# 最適化されたパラメータの出力
a_opt, b_opt, c_opt = params
print(f"最適化されたパラメータ: a={a_opt:.4f}, b={b_opt:.4f}, c={c_opt:.4f}")

# 滑らかな曲線のための細かい温度ポイント
temp_fine = np.linspace(0, 100, 1000)
heat_fine = fitting_function(temp_fine, *params)

# グラフの描画
plt.figure(figsize=(5, 4))
plt.plot(temp_fine, heat_fine, 'k-', linewidth=2)

# グラフの設定
plt.xlim(0, 100)
plt.ylim(0, 3.1)
plt.grid(True)
plt.xlabel('Temperature (K)', fontsize=14)
plt.ylabel('C/R', fontsize=14)
plt.xticks([0, 50, 100])
plt.yticks([0, 1, 2, 3])

# グリッド線を追加
plt.axhline(y=1, color='black', linestyle='-', alpha=0.5)
plt.axhline(y=2, color='black', linestyle='-', alpha=0.5)
plt.axhline(y=3, color='black', linestyle='-', alpha=0.5)
plt.axvline(x=50, color='black', linestyle='-', alpha=0.5)
plt.axvline(x=100, color='black', linestyle='-', alpha=0.5)

# サンプリングポイントは表示しない

# グラフを表示
plt.tight_layout()
plt.savefig('heat_capacity_curve.png', dpi=300)
plt.show()

# 重要な温度ポイントでの値を確認
check_temps = [0, 5, 10, 50, 100]
for temp in check_temps:
    value = fitting_function(temp, *params)
    print(f"温度 {temp}K での C/R: {value:.4f}")