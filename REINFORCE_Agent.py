import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions.categorical import Categorical

class Memory:
    '''
    the memory get tensors onlt
    '''
    def __init__(self, device):
        self.states = []
        self.actions = []
        self.rewards = []
        self.divice = device
    
    def store_memory (self, state, action, reward):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)

    def clear_memory (self):
        self.states = []
        self.actions = []
        self.rewards = []
    
    def get_tensors(self):
        states_tensor = torch.stack(self.states).to(self.divice)
        actions_tensor = torch.stack(self.actions).to(self.divice)
        rewards_tensor = torch.stack(self.rewards).to(self.divice)
        self.clear_memory()
        return states_tensor, actions_tensor, rewards_tensor
    

class REINFORCE_Network (nn.Module):
    def __init__(self, state_dim, action_dim, lr=0.001, fc_dims=256, chkpt=1, optim_step = 100, optim_gamma = 0.9):
        super().__init__()
        self.linear1 = nn.Linear(state_dim, fc_dims)
        self.Relu = nn.ReLU()
        self.linear2 = nn.Linear(fc_dims, fc_dims)
        self.linear3 = nn.Linear(fc_dims, action_dim)
        self.mean_layer = nn.Linear(fc_dims, action_dim)
        self.std_layer = nn.Linear(fc_dims, action_dim)
        self.lr = lr
        self.optimizer = optim.Adam(self.parameters(), lr=lr)  
        # self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=optim_step, gamma=optim_gamma)
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.to(self.device)
        self.checkpoint_file = f'Data/REINFORCE{chkpt}.pth'
        
        
    def forward(self, state):
        x = self.linear1(state)
        x = self.Relu(x)
        x = self.linear2(x)
        x = self.Relu(x)
        mean = torch.tanh(self.mean_layer(x)) # between (-1,1)
        std = F.softplus(self.std_layer(x)) + 1e-6
        return mean, std
    
    def load_params(self):
        self.load_state_dict(torch.load(self.checkpoint_file, weights_only=True))

    def save_params(self):
        torch.save(self.state_dict(), self.checkpoint_file)


class REINFORCE_Agent:
    def __init__(self, chkpt, player = 1, state_dim = 14, action_dim=2  ):
        self.policy = REINFORCE_Network(chkpt=chkpt, state_dim=state_dim, action_dim=action_dim)
        self.player = player
        self.memory = Memory(self.policy.device)
        self.gamma = 0.95
        self.entropy_coe = 0.1
        
        self.sum_loss = 0  # for logging
        self.sum_entropy = 0 # for logging
        

    def remember (self, state, action, reward):
        '''
        reward (float)
        prob (tensor)
        '''
        self.memory.store_memory(state, torch.tensor(action), torch.tensor(reward))

    def save_model(self):
        self.policy.save_params()

    def load_model(self):
        self.policy.load_params()

    def get_action(self, state, events = None, train = None):
        state_tensor = state.to(self.policy.device)
        with torch.no_grad():
            mean, std = self.policy(state_tensor)
        
        dist = torch.distributions.Normal(mean, std)
        action = dist.rsample()
        F_thrust, T_spin = action.tolist()
        return F_thrust, T_spin

    def get_actions_logs (self, states_tensor):
        states_tensor = states_tensor.to(self.policy.device)
        mean, std = self.policy(states_tensor)
        dist = torch.distributions.Normal(mean, std)
        actions = dist.rsample()
        log_probs = dist.log_prob(actions).sum(dim=-1) 
        return actions, log_probs

    def to_action(self, action_index):
        row = action_index // 3
        col = action_index % 3
        return row, col
    

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
                            
        # Convert action_probs from list of 1 item tensor to a tensor 
        dist = self.get_actions_logs(states)
        log_probs = dist.log_prob(actions)
        
                
        # Compute the loss using vectorized operations
        policy_loss = -(G * log_probs).sum()
        
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
        return self.choose_action(*args)


    

    