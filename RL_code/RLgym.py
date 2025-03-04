import gym
import math
import random
import time
import torch
import torch.nn as nn
import torch.optim as optim
from collections import namedtuple, deque

# ハイパーパラメータ
BATCH_SIZE = 128
GAMMA = 0.99
EPS_START = 1.0
EPS_END = 0.01
EPS_DECAY = 500
TARGET_UPDATE = 10
LR = 1e-3
NUM_EPISODES = 500

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

Transition = namedtuple(
    'Transition',
    ('state', 'action', 'next_state', 'reward')
)


class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(n_observations, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, n_actions)
        )

    def forward(self, x):
        return self.fc(x)


def select_action(state, policy_net, steps_done, n_actions):
    # ε-greedy ポリシー
    eps_threshold = EPS_END + (EPS_START - EPS_END) * (
        math.exp(-1. * steps_done / EPS_DECAY)
    )
    if random.random() > eps_threshold:
        with torch.no_grad():
            return policy_net(state).max(1)[1].view(1, 1)
    else:
        return torch.tensor(
            [[random.randrange(n_actions)]],
            device=device,
            dtype=torch.long
        )


def optimize_model(policy_net, target_net, memory, optimizer):
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))

    non_final_mask = torch.tensor(
        tuple(map(lambda s: s is not None, batch.next_state)),
        device=device,
        dtype=torch.bool
    )
    non_final_next_states = torch.cat(
        [s for s in batch.next_state if s is not None]
    )

    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    state_action_values = policy_net(state_batch).gather(1, action_batch)

    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    next_state_values[non_final_mask] = (
        target_net(non_final_next_states)
        .max(1)[0]
        .detach()
    )

    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    criterion = nn.SmoothL1Loss()
    loss = criterion(
        state_action_values,
        expected_state_action_values.unsqueeze(1)
    )

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


def main():
    env = gym.make("CartPole-v1")
    state = env.reset()
    if isinstance(state, tuple):  # gym >=0.26 の場合
        state, _ = state

    n_actions = env.action_space.n
    n_observations = env.observation_space.shape[0]

    policy_net = DQN(n_observations, n_actions).to(device)
    target_net = DQN(n_observations, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()

    optimizer = optim.Adam(policy_net.parameters(), lr=LR)
    memory = ReplayMemory(10000)

    steps_done = 0
    for i_episode in range(NUM_EPISODES):
        state = env.reset()
        if isinstance(state, tuple):
            state, _ = state
        state = torch.tensor([state], device=device, dtype=torch.float)
        total_reward = 0
        for t in range(1, 10000):
            env.render()  # 可視化: 各ステップで描画
            action = select_action(state, policy_net, steps_done, n_actions)
            steps_done += 1
            result = env.step(action.item())
            if len(result) == 5:
                next_state, reward, done, truncated, _ = result
                done = done or truncated
            else:
                next_state, reward, done, _ = result
            total_reward += reward
            reward_tensor = torch.tensor(
                [reward],
                device=device,
                dtype=torch.float
            )
            if not done:
                next_state_tensor = torch.tensor(
                    [next_state],
                    device=device,
                    dtype=torch.float
                )
            else:
                next_state_tensor = None
            memory.push(state, action, next_state_tensor, reward_tensor)
            if next_state_tensor is not None:
                state = next_state_tensor
            else:
                state = torch.tensor(
                    [next_state],
                    device=device,
                    dtype=torch.float
                )

            optimize_model(policy_net, target_net, memory, optimizer)

            if done:
                print(
                    f"Episode {i_episode} finished after {t} timesteps, "
                    f"total reward: {total_reward}"
                )
                break
            time.sleep(0.02)

        if i_episode % TARGET_UPDATE == 0:
            target_net.load_state_dict(policy_net.state_dict())
    print("Training complete")
    env.close()

    # 学習済みモデルを用いて可視化（テスト）する部分
    test_env = gym.make("CartPole-v1", render_mode="rgb_array")
    try:
        # RecordVideo を使って動画を保存（video フォルダに保存されます）
        test_env = gym.wrappers.RecordVideo(
            test_env, video_folder="./video", name_prefix="dqn-cartpole-demo"
        )
    except gym.error.DependencyNotInstalled:
        print("MoviePyがインストールされていないため、動画記録をスキップします。")

    state = test_env.reset()
    if isinstance(state, tuple):
        state, _ = state
    state = torch.tensor([state], device=device, dtype=torch.float)
    done = False
    while not done:
        # test_env.render() は RecordVideo ラッパーでは不要（または呼び出すとエラーになるため削除）
        with torch.no_grad():
            action = policy_net(state).max(1)[1].view(1, 1)
        result = test_env.step(action.item())
        if len(result) == 5:
            next_state, reward, done, truncated, _ = result
            done = done or truncated
        else:
            next_state, reward, done, _ = result
        if not done:
            state = torch.tensor(
                [next_state],
                device=device,
                dtype=torch.float
            )
        time.sleep(0.02)
    test_env.close()


if __name__ == '__main__':
    main()
