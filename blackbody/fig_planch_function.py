import numpy as np
import matplotlib.pyplot as plt

# プランク関数の定義
def planck_function(x):
    # x=0での特異点を避けるため、非常に小さい値ではテイラー展開の第一項を使用
    mask = x < 1e-10
    result = np.empty_like(x, dtype=float)
    result[mask] = 1.0  # x→0 で x/(e^x-1) → 1
    # 通常の計算
    mask = ~mask
    result[mask] = x[mask] / (np.exp(x[mask]) - 1.0)
    return result

# xの範囲設定
x_min = 0.01  # 0に近すぎると特異点に近づくため、少し離す
x_max = 10    # 十分大きな値まで
x = np.linspace(x_min, x_max, 1000)

# プランク関数の計算
y = planck_function(x)

# グラフ描画
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'k-', linewidth=2)

# グラフの設定
plt.xlabel('x', fontsize=18)
plt.ylabel('f(x) = x/(e$^x$-1)', fontsize=18)
# plt.title('プランク関数 f(x) = x/(e$^x$-1)', fontsize=16)
plt.grid(True, alpha=0.3)
plt.xlim(0, x_max)
plt.ylim(0, 1.1)  # 関数の最大値は1なので、少し余裕を持たせる

# 座標軸の目盛りラベルのフォントサイズを大きく設定
plt.xticks(fontsize=16)  # X軸の数字サイズ
plt.yticks(fontsize=16)  # Y軸の数字サイズ

# 座標軸の設定
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)

# 特徴的な点にマーカーを設置
plt.scatter([0], [1], color='red', s=50, zorder=3)
plt.annotate('f(0)=1', xy=(0.2, 0.9), fontsize=14)

# 保存と表示
plt.tight_layout()
plt.savefig('planck_function.png', dpi=300)
plt.show()

# 数学的特性の出力
print("プランク関数 f(x) = x/(e^x-1) の特性値:")
print(f"f(0) = 1 (極限値)")
x_samples = [0.1, 1.0, 2.0, 5.0, 10.0]
for x in x_samples:
    print(f"f({x}) = {planck_function(np.array([x]))[0]:.6f}")
