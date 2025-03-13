import torch
from torch.distributions import Normal

mean, std = torch.tensor([0.2, -0.1]), torch.tensor([1.5, 1.2])
dist = Normal(mean, std)

sample = dist.sample()       # Normal sampling
sample = dist.rsample()      # Normal sampling with gradients

prob = dist.log_prob(x)      # Log probability of value x
entropy = dist.entropy()     # Entropy of the distribution


