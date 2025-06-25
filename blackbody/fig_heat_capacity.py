import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from scipy.optimize import curve_fit
import matplotlib.gridspec as gridspec

# === データの準備 ===
# 三次スプライン補間用のデータ (specific_heat.py)
spline_temp_points = np.array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300])
spline_CpR_points = np.array([1.50, 1.50, 1.51, 1.53, 1.60, 1.75, 1.95, 2.12, 2.25, 2.33, 2.38, 2.41, 2.44, 2.46, 2.48, 2.49])

# シグモイドフィッティング用のデータ (pb_sh.py)
sigmoid_temperatures = np.array([0, 2, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100])
sigmoid_specific_heats = np.array([0, 0.05, 0.2, 0.52, 0.95, 1.45, 1.9, 2.25, 2.5, 2.7, 2.85, 2.92, 2.96, 2.98, 2.99, 3.0])

# === モデル計算 ===
# 三次スプライン補間
cs = CubicSpline(spline_temp_points, spline_CpR_points)
spline_temperatures = np.linspace(0, 300, 300)
spline_CpR_smooth = cs(spline_temperatures)

# シグモイドフィッティング関数
def fitting_function(x, a, b, c):
    return a * (1 - np.exp(-b * x**c))

# シグモイドフィッティング実行
initial_params = [3.0, 0.01, 1.5]
params, _ = curve_fit(fitting_function, sigmoid_temperatures, sigmoid_specific_heats, p0=initial_params)
a_opt, b_opt, c_opt = params

# シグモイド曲線の計算
sigmoid_temp_fine = np.linspace(0, 100, 1000)
sigmoid_heat_fine = fitting_function(sigmoid_temp_fine, *params)

# === プロットの作成 ===
plt.figure(figsize=(12, 5))
gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])

# 共通スタイル設定関数 (タイトルなし)
def apply_common_style(ax, xlabel="Temperature (K)", ylabel="C/R"):
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, color='black', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return ax

# 1. 三次スプライン補間のプロット（左側）
ax1 = plt.subplot(gs[0])
ax1.plot(spline_temperatures, spline_CpR_smooth, 'k-', linewidth=2)
ax1.scatter(spline_temp_points, spline_CpR_points, color='#444444', s=30, alpha=0.8)
ax1 = apply_common_style(ax1)
ax1.set_xlim(0, 300)
ax1.set_ylim(1.5, 2.5)
ax1.set_yticks([1.5, 2.0, 2.5])

# グリッド線を追加（スプライン側）
ax1.axhline(y=1.5, color='black', linestyle='-', alpha=0.3)
ax1.axhline(y=2.0, color='black', linestyle='-', alpha=0.3)
ax1.axhline(y=2.5, color='black', linestyle='-', alpha=0.3)
ax1.axvline(x=100, color='black', linestyle='-', alpha=0.3)
ax1.axvline(x=200, color='black', linestyle='-', alpha=0.3)
ax1.axvline(x=300, color='black', linestyle='-', alpha=0.3)

# 2. シグモイドフィットのプロット（右側）
ax2 = plt.subplot(gs[1])
ax2.plot(sigmoid_temp_fine, sigmoid_heat_fine, 'k-', linewidth=2)
ax2.scatter(sigmoid_temperatures, sigmoid_specific_heats, color='#444444', s=30, alpha=0.8)
ax2 = apply_common_style(ax2)
ax2.set_xlim(0, 100)
ax2.set_ylim(0, 3.1)
ax2.set_xticks([0, 50, 100])
ax2.set_yticks([0, 1, 2, 3])

# グリッド線を追加（シグモイド側）
ax2.axhline(y=1, color='black', linestyle='-', alpha=0.3)
ax2.axhline(y=2, color='black', linestyle='-', alpha=0.3)
ax2.axhline(y=3, color='black', linestyle='-', alpha=0.3)
ax2.axvline(x=50, color='black', linestyle='-', alpha=0.3)
ax2.axvline(x=100, color='black', linestyle='-', alpha=0.3)

# 共通の調整
plt.tight_layout()
plt.subplots_adjust(wspace=0.3)  # グラフ間の間隔調整

# 保存と表示
#plt.savefig('combined_heat_curves.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
plt.savefig('heat_capacity.png', dpi=300)
plt.show()

# 結果の数値比較
print("=== シグモイドフィットの比熱曲線 ===")
print(f"最適化されたパラメータ: a={a_opt:.4f}, b={b_opt:.4f}, c={c_opt:.4f}")
check_temps = [0, 20, 40, 60, 80, 100]
for temp in check_temps:
    value = fitting_function(temp, *params)
    print(f"温度 {temp}K での C/R: {value:.4f}")

print("\n=== 三次スプライン補間の比熱曲線 ===")
for temp in check_temps:
    value = cs(temp)
    print(f"温度 {temp}K での C/R: {value:.4f}")
    
    
