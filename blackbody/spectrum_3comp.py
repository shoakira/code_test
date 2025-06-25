import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# 物理定数
h = 6.626e-34  # プランク定数 [J・s]
c = 2.998e8    # 光速 [m/s]
k = 1.381e-23  # ボルツマン定数 [J/K]

# プランクの放射公式
def planck_formula(nu, T):
    """
    nu: 周波数 [Hz]
    T: 温度 [K]
    返り値: エネルギー密度 [J/(m^3・Hz)]
    """
    return (8 * np.pi * h * nu**3) / (c**3) * (1 / (np.exp((h * nu) / (k * T)) - 1))

# レーリー-ジーンズの公式（低周波近似）
def rayleigh_jeans_formula(nu, T):
    """
    nu: 周波数 [Hz]
    T: 温度 [K]
    返り値: エネルギー密度 [J/(m^3・Hz)]
    """
    return (8 * np.pi * nu**2 * k * T) / (c**3)

# ウィーンの公式（高周波近似）
def wien_formula(nu, T):
    """
    nu: 周波数 [Hz]
    T: 温度 [K]
    返り値: エネルギー密度 [J/(m^3・Hz)]
    """
    return (8 * np.pi * h * nu**3) / (c**3) * np.exp(-(h * nu) / (k * T))

# 1つの温度を使用
T = 2500  # 温度 [K]

# 周波数の範囲を調整
# プランクの法則の最大値を計算 (Wien's displacement law)
nu_max = 2.821 * k * T / h

# 周波数範囲を調整 - 比較しやすいように
# 線形スケール用 - 最大値の前後を広く取る
nu_linear = np.linspace(0.05 * nu_max, 4 * nu_max, 1000)  

# 対数スケール用 - より広い範囲をカバー
nu_log = np.logspace(np.log10(0.01 * nu_max), np.log10(10 * nu_max), 1000)

# 各放射公式の計算
# プランクの公式
p_intensity = planck_formula(nu_linear, T)
p_intensity_log = planck_formula(nu_log, T)

# レーリー-ジーンズの公式
rj_intensity = rayleigh_jeans_formula(nu_linear, T)
rj_intensity_log = rayleigh_jeans_formula(nu_log, T)

# ウィーンの公式
w_intensity = wien_formula(nu_linear, T)
w_intensity_log = wien_formula(nu_log, T)

# グラフの作成
fig = plt.figure(figsize=(12, 6))
gs = GridSpec(1, 2, figure=fig)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# 線形スケールのプロット (左側)
ax1.plot(nu_linear, p_intensity, 'b-', linewidth=2.5, label='Planck')
ax1.plot(nu_linear, rj_intensity, 'r--', linewidth=2, label='Rayleigh-Jeans')
ax1.plot(nu_linear, w_intensity, 'g:', linewidth=2, label='Wien')

# 対数スケールのプロット (右側)
ax2.loglog(nu_log, p_intensity_log, 'b-', linewidth=2.5, label='Planck')
ax2.loglog(nu_log, rj_intensity_log, 'r--', linewidth=2, label='Rayleigh-Jeans')
ax2.loglog(nu_log, w_intensity_log, 'g:', linewidth=2, label='Wien')

# 最大値位置の縦線を追加
ax1.axvline(x=nu_max, color='gray', linestyle='-', alpha=0.5, label='Peak frequency')
ax2.axvline(x=nu_max, color='gray', linestyle='-', alpha=0.5)

# タイトルと軸ラベル
title_text = f'Blackbody Radiation Formulas Comparison at {T}K'
fig.suptitle(title_text, fontsize=14)

ax1.set_title('Linear Scale')
ax1.set_xlabel('Frequency [Hz]')
ax1.set_ylabel('Energy Density [J/(m³·Hz)]')
ax1.set_ylim(0, 0.3e-15)  # 縦軸の上限を0.1×10^-14に設定
ax1.grid(True, linestyle='--', alpha=0.7)

# x軸のフォーマットを科学表記に
ax1.ticklabel_format(axis='x', style='sci', scilimits=(0,0))

ax2.set_title('Log-Log Scale')
ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Energy Density [J/(m³·Hz)]')
ax2.grid(True, which="both", linestyle='--', alpha=0.7)

# 凡例
ax1.legend(loc='upper right')
ax2.legend(loc='lower left')

# 保存と表示
plt.tight_layout()
plt.savefig('blackbody_formulas_comparison.png', dpi=150, bbox_inches='tight')
plt.show()