import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Normal

class Memory: 
    '''
    the memory get tensors onlt
    '''
    def __init__(self, device):
        self.states = []
        self.actions = []
        self.rewards = []
        self.device = device
    
    def store_memory (self, state, action, reward):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)

    def clear_memory (self):
        self.states = []
        self.actions = []
        self.rewards = []
    
    def get_tensors(self):
        states_tensor = torch.stack(self.states).to(self.device)
        actions_tensor = torch.stack(self.actions).to(self.device)
        rewards_tensor = torch.stack(self.rewards).to(self.device)
        self.clear_memory()
        return states_tensor, actions_tensor, rewards_tensor

class REINFORCE_Network (nn.Module):
    def __init__(self, state_dim, action_dim, lr=0.00001, fc_dims=256, chkpt=1):
        super().__init__()
        self.linear1 = nn.Linear(state_dim, fc_dims)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(fc_dims, fc_dims)
        self.mean_layer = nn.Linear(fc_dims, action_dim)
        self.std_layer = nn.Linear(fc_dims, action_dim)
        self.lr = lr
        self.optimizer = optim.Adam(self.parameters(), lr=lr)  
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.to(self.device)
        self.checkpoint_file = f'Data/REINFORCE{chkpt}.pth'
        
    def forward(self, state):
        x = self.relu(self.linear1(state))
        x = self.relu(self.linear2(x))

        mean_raw = self.mean_layer(x)
        thrust_mean = (torch.tanh(mean_raw[:, 0]) + 1) / 2  # Thrust in [0,1]
        spin_mean = torch.tanh(mean_raw[:, 1])              # Spin in [-1,1]
        mean = torch.stack([thrust_mean, spin_mean], dim=1)
        std = F.softplus(self.std_layer(x)) + 1e-6          # Ensure std is positive
        return mean, std
    
    def load_params(self):
        self.load_state_dict(torch.load(self.checkpoint_file))

    def save_params(self):
        torch.save(self.state_dict(), self.checkpoint_file)

class REINFORCE_Agent:
    def __init__(self, chkpt, player = 1, state_dim = 11, action_dim=2  ):
        self.policy = REINFORCE_Network(chkpt=chkpt, state_dim=state_dim, action_dim=action_dim)
        self.player = player
        self.memory = Memory(self.policy.device)
        self.gamma = 0.995
        self.entropy_coe = 0.1
        
        self.sum_loss = 0  # for logging
        self.sum_entropy = 0 # for logging

    def remember (self, state, action, reward):
        '''
        reward (float)
        prob (tensor)
        '''
        self.memory.store_memory(state, action, torch.tensor(reward))

    def save_model(self):
        self.policy.save_params()

    def load_model(self):
        self.policy.load_params()

    def get_action(self, state, events = None, train = False):
        state_tensor = state.to(self.policy.device).view(1,-1)
        with torch.no_grad():
            mean, std = self.policy(state_tensor)
        mean = mean.squeeze(0)
        std = std.squeeze(0)
        dist = Normal(mean, std)
        action = dist.rsample()
        action = action.clamp(min=torch.tensor([0, -1], device=self.policy.device),
                              max=torch.tensor([1, 1], device=self.policy.device))
        
        thrust, spin = action[0].item(), action[1].item()

        if train:
            return (thrust, spin), action
        return thrust, spin
    
    def get_dist (self, states_tensor):
        states_tensor = states_tensor.to(self.policy.device)
        mean, std = self.policy(states_tensor)
        dist = Normal(mean, std)
        return dist
    
    def compute_G (self, rewards):
        G_returns = torch.zeros_like(rewards)
        G = 0
        for i in range(rewards.size(0)-1, -1, -1):   # in reverse
            G = rewards[i] + self.gamma * G
            G_returns[i]= G
        
        return G_returns
    
    def learn(self):
        
        states, actions, rewards = self.memory.get_tensors()
        
        G = self.compute_G(rewards)
                            
        dist = self.get_dist(states)
        log_probs = dist.log_prob(actions).sum(dim=-1)
                
        # Compute the loss using vectorized operations
        policy_loss = -(G * log_probs).mean()
        
        # Add Entropy regularization
        entropy = dist.entropy().mean()
        loss = policy_loss - self.entropy_coe * entropy 
       

        # backward
        self.policy.optimizer.zero_grad()
        loss.backward()
        
        self.policy.optimizer.step()

        #### for logging
        self.sum_loss += loss.detach()
        self.sum_entropy += dist.entropy().detach().mean()
    
    def __call__(self, *args, **kwds):
        return self.get_action(*args)


    