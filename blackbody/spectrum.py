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

# レーリー-ジーンズの公式
def rayleigh_jeans_formula(nu, T):
    """
    nu: 周波数 [Hz]
    T: 温度 [K]
    返り値: エネルギー密度 [J/(m^3・Hz)]
    """
    return (8 * np.pi * nu**2 * k * T) / (c**3)

# 3つの温度
T1 = 1000  # 温度1 [K]
T2 = 2500  # 温度2 [K]
T3 = 4000  # 温度3 [K]

# 周波数の範囲
nu_linear = np.linspace(1e11, 3e14, 1000)  # 線形スケール用
nu_log = np.logspace(11, 14.5, 1000)  # 対数スケール用

# 各温度での放射強度を計算
# プランクの公式
p_intensity1 = planck_formula(nu_linear, T1)
p_intensity2 = planck_formula(nu_linear, T2)
p_intensity3 = planck_formula(nu_linear, T3)

# レーリー-ジーンズの公式
rj_intensity1 = rayleigh_jeans_formula(nu_linear, T1)
rj_intensity2 = rayleigh_jeans_formula(nu_linear, T2)
rj_intensity3 = rayleigh_jeans_formula(nu_linear, T3)

# 対数スケール用
p_intensity1_log = planck_formula(nu_log, T1)
p_intensity2_log = planck_formula(nu_log, T2)
p_intensity3_log = planck_formula(nu_log, T3)

rj_intensity1_log = rayleigh_jeans_formula(nu_log, T1)
rj_intensity2_log = rayleigh_jeans_formula(nu_log, T2)
rj_intensity3_log = rayleigh_jeans_formula(nu_log, T3)

# グラフの作成 - サイズを制限
fig = plt.figure(figsize=(10, 5))
gs = GridSpec(1, 2, figure=fig)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# 線形スケールのプロット (左側)
ax1.plot(nu_linear, p_intensity1, 'b-', linewidth=2, label=f'P {T1}K')
ax1.plot(nu_linear, p_intensity2, 'g-', linewidth=2, label=f'P {T2}K')
ax1.plot(nu_linear, p_intensity3, 'r-', linewidth=2, label=f'P {T3}K')

ax1.plot(nu_linear, rj_intensity1, 'b--', linewidth=1.5, label=f'RJ {T1}K')
ax1.plot(nu_linear, rj_intensity2, 'g--', linewidth=1.5, label=f'RJ {T2}K')
ax1.plot(nu_linear, rj_intensity3, 'r--', linewidth=1.5, label=f'RJ {T3}K')

# 対数スケールのプロット (右側)
ax2.loglog(nu_log, p_intensity1_log, 'b-', linewidth=2)
ax2.loglog(nu_log, p_intensity2_log, 'g-', linewidth=2)
ax2.loglog(nu_log, p_intensity3_log, 'r-', linewidth=2)

ax2.loglog(nu_log, rj_intensity1_log, 'b--', linewidth=1.5)
ax2.loglog(nu_log, rj_intensity2_log, 'g--', linewidth=1.5)
ax2.loglog(nu_log, rj_intensity3_log, 'r--', linewidth=1.5)

# 軸ラベルとタイトル (英語のみ)
ax1.set_title('Linear Scale')
ax1.set_xlabel('Frequency [Hz]')
ax1.set_ylabel('Energy Density [J/(m³·Hz)]')
ax1.set_xlim(0, 3e14)
ax1.set_ylim(0, max(p_intensity3) * 1.1)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.set_xticks([0, 1e14, 2e14, 3e14])
ax1.set_xticklabels(['0', '1×10¹⁴', '2×10¹⁴', '3×10¹⁴'])

ax2.set_title('Log-Log Scale')
ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Energy Density [J/(m³·Hz)]')
ax2.set_xlim(1e11, 3e14)
ax2.grid(True, which="both", linestyle='--', alpha=0.7)



# 保存と表示 - サイズとDPIを明示的に制限
plt.tight_layout()
plt.savefig('blackbody_radiation_comparison.png', dpi=150, bbox_inches='tight')
plt.show()