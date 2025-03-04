import os
import gym
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.distributions as distributions
import matplotlib.pyplot as plt  # グラフ描画用
import warnings

# matplotlib のユーザー警告を無視
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
# すべての「Glyph ... missing from font」警告を無視
warnings.filterwarnings("ignore", message="Glyph .* missing from font.*")
# np.bool8 の非推奨警告を無視
warnings.filterwarnings("ignore", message="`np.bool8` is a deprecated alias for `np.bool_`")

# 日本語表示のためのフォント設定（Macの場合はAppleGothicを利用）
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# ハイパーパラメータの設定
LR = 1e-3              # 学習率
NUM_EPISODES = 100     # エピソード数
GAMMA = 0.98           # 割引率

# 使用するデバイス（GPUがあればGPU、なければCPU）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# チェックポイントファイル
CHECKPOINT_PATH = "policy_net_checkpoint.pth"

# Policy Network: 状態を入力し、各行動の確率分布を出力する
class PolicyNet(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(PolicyNet, self).__init__()
        # 全結合層1: 状態次元を128に変換
        self.fc1 = nn.Linear(n_observations, 128)
        # 全結合層2: 隠れ層から行動数に変換
        self.fc2 = nn.Linear(128, n_actions)
    
    def forward(self, x):
        # fc1の出力にReLU活性化関数を適用
        x = F.relu(self.fc1(x))
        # fc2出力にsoftmaxを適用し、各行動の確率分布を得る
        return F.softmax(self.fc2(x), dim=-1)

# 方策に従って行動を選択し、選択した行動の対数確率も返す関数
def select_action(policy_net, state):
    probs = policy_net(state)
    m = distributions.Categorical(probs)
    action = m.sample()
    return action, m.log_prob(action)

# エピソード終了後、報酬のリストから各時刻の割引累積報酬（Return）を計算する関数
def compute_returns(rewards, gamma):
    R = 0
    returns = []
    for r in reversed(rewards):
        R = r + gamma * R
        returns.insert(0, R)
    return returns

def main():
    env = gym.make("CartPole-v1", render_mode="human")
    n_observations = env.observation_space.shape[0]
    n_actions = env.action_space.n

    policy_net = PolicyNet(n_observations, n_actions).to(device)
    optimizer = optim.Adam(policy_net.parameters(), lr=LR)
    
    if os.path.exists(CHECKPOINT_PATH):
        policy_net.load_state_dict(torch.load(CHECKPOINT_PATH))
        print("Checkpoint loaded, resuming training...")
    
    episode_rewards = []
    
    for i_episode in range(NUM_EPISODES):
        state = env.reset()
        if isinstance(state, tuple):
            state, _ = state
        # torch.as_tensor を利用して numpy 配列から tensor に変換（必要に応じてコピーしない）
        state = torch.as_tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        
        log_probs = []
        rewards = []
        total_reward = 0
        done = False
        t = 0
        while not done:
            action, log_prob = select_action(policy_net, state)
            result = env.step(action.item())
            if len(result) == 5:
                next_state, reward, terminated, truncated, _ = result
                done = terminated or truncated
            else:
                next_state, reward, done, _ = result
            total_reward += reward
            log_probs.append(log_prob)
            rewards.append(reward)
            if not done:
                state = torch.as_tensor(next_state, dtype=torch.float32, device=device).unsqueeze(0)
            t += 1

        # 損失計算をベクトル演算で実施
        returns = compute_returns(rewards, GAMMA)
        returns = torch.as_tensor(returns, dtype=torch.float32, device=device)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        loss = - (torch.stack(log_probs) * returns).sum()
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        episode_rewards.append(total_reward)
        print(f"Episode {i_episode} finished after {t} timesteps, total reward: {total_reward}")
    
    env.close()
    torch.save(policy_net.state_dict(), CHECKPOINT_PATH)
    print("Checkpoint saved.")
    
    plt.figure(figsize=(10, 5))
    plt.plot(episode_rewards, label="Total Reward", color="blue")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("Total Reward per Episode")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == '__main__':
    main()
