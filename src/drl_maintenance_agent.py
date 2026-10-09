"""
IMS Deep Reinforcement Learning (DRL) Autonomous Maintenance Agent (DQN / PPO)
Trains a Deep Q-Network agent to autonomously decide optimal maintenance interventions (0: Run, 1: Derate RPM, 2: Emergency Replace).
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import MODELS_DIR

class DQNMaintenanceAgent(nn.Module):
    """Deep Q-Network predicting Q-values for 3 discrete actions."""
    def __init__(self, state_dim: int = 4, action_dim: int = 3):
        super(DQNMaintenanceAgent, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, action_dim) # Actions: 0=RUN_NORMAL, 1=DERATE_RPM_50PCT, 2=EMERGENCY_REPLACE
        )

    def forward(self, state):
        return self.net(state)

def train_dqn_agent(episodes: int = 30) -> str:
    """Trains Deep Q-Network on simulated industrial environment."""
    print(f"[INFO] Training Deep Reinforcement Learning (DRL) Maintenance Agent ({episodes} Episodes)...")

    agent = DQNMaintenanceAgent(state_dim=4, action_dim=3)
    optimizer = optim.Adam(agent.parameters(), lr=0.003)
    criterion = nn.MSELoss()

    action_labels = ["RUN_NORMAL", "DERATE_RPM_50PCT", "EMERGENCY_REPLACE"]

    for ep in range(1, episodes + 1):
        # Simulated environment state: [RMS, Kurtosis, Temp, RUL]
        state = torch.tensor([np.random.uniform(0.05, 0.7), np.random.uniform(3.0, 9.0), np.random.uniform(35, 80), np.random.uniform(5, 160)], dtype=torch.float32)
        
        optimizer.zero_grad()
        q_values = agent(state)
        action = torch.argmax(q_values).item()

        # Reward structure: Reward high uptime, penalize downtime and catastrophic failure
        target_q = q_values.clone().detach()
        if state[0] > 0.5 and action == 0:
            reward = -100.0 # Catastrophic failure penalty
        elif state[0] > 0.5 and action == 2:
            reward = +50.0  # Timely replacement reward
        else:
            reward = +10.0  # Normal operation reward

        target_q[action] = reward
        loss = criterion(q_values, target_q)
        loss.backward()
        optimizer.step()

        if ep % 10 == 0 or ep == episodes:
            print(f"Episode {ep:2d}/{episodes} | Selected Action: {action_labels[action]} | Loss: {loss.item():.4f}")

    output_path = os.path.join(MODELS_DIR, "dqn_drl_maintenance_agent.pth")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(agent.state_dict(), output_path)

    print(f"[SUCCESS] DRL Maintenance Agent saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    train_dqn_agent()
