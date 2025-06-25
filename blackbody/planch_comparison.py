import numpy as np
import matplotlib.pyplot as plt

# 定数（SI単位系）
h = 6.62607015e-34       # プランク定数 [J s]
c = 2.99792458e8         # 光速度 [m/s]
k = 1.380649e-23         # ボルツマン定数 [J/K]

# 温度の設定（例：5000 K）
T = 5000

# 波長範囲の設定 (例：100 nm 〜 3000 nm)
# SI単位では [m]: 1e-7 m 〜 3e-6 m
lam = np.linspace(1e-7, 3e-6, 500)  # 波長 [m]

# プランクの分光放射輝度 (単位: J s^-1 m^-2 sr^-1 m^-1)
U_planck = (8 * np.pi * h * c) / (lam**5) / (np.exp((h*c)/(lam*k*T)) - 1)

# レイリー・ジーンズの近似式 (波長表示)
U_RJ = (8 * np.pi * k * T) / (lam**4)

# ウィーンの近似式 (波長表示)
U_W = (8 * np.pi * h * c) / (lam**5) * np.exp(-(h*c)/(lam*k*T))

# 波長をナノメートル単位に変換
lam_nm = lam * 1e9

# グラフの描画
plt.figure(figsize=(8, 6))
plt.plot(lam_nm, U_planck, label="Planck's law", color="black")
plt.plot(lam_nm, U_RJ, label="Rayleigh-Jeans law", linestyle="--", color="red")
plt.plot(lam_nm, U_W, label="Wien's law", linestyle=":", color="blue")

plt.xlabel("Wavelength (nm)")
plt.ylabel("Spectral energy density")
plt.title(f"Blackbody radiation at T = {T} K")
plt.legend()
plt.grid(True)
plt.yscale("log")  # 対数スケールで表示すると各式の違いが見やすい
plt.show()
