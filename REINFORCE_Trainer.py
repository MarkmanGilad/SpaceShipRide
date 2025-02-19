import torch
import random
import pygame
from REINFORCE_Agent import REINFORCE_Agent
from Environment import SpaceShipRide
import wandb
from collections import deque
 

class REINFORCE_Trainer:
    def __init__(self,  chkpt):
        self.agent:REINFORCE_Agent = REINFORCE_Agent(chkpt=chkpt)
        self.env:SpaceShipRide = SpaceShipRide()
        self.chkpt = chkpt

    def train(self, epochs=100000, gamma = 0.99, lr=0.001):
        self.init_wandb(project_name="REINFORCE-continuous",chkpt=self.chkpt,resume=False)
        score = 0
        losses = []
        for epoch in range(epochs):
            print(epoch, end="\r")
            state = self.env.restart()
            self.env.step = 0
            self.env.done = False
            ########### sample environment ###########
            while not self.env.done:
                self.env.step += 1
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                pygame.event.pump()
                state = self.env.get_state()
                action = (0.1, random.random()-0.5) #self.agent.get_action()
                self.env.render(action)
                reward = self.env.get_reward()
                
                #reward2 += reward1
                self.agent.remember(state, action, reward)
                
            
            ########### train ###########
            print (f"\nstep: {self.env.step} reward: {self.env.get_reward()} ")
            self.agent.learn()

            ########### log ###########
            score += reward
            if epoch !=0 and epoch % 100 == 0:
                self.log_wandb(score=score, loss = self.agent.sum_loss/100, entropy = self.agent.sum_entropy/100)
                print (f'chkpt: {self.chkpt} epoch: {epoch} score: {score} loss: {self.agent.sum_loss/100:.4e} entropy: {self.agent.sum_entropy/100:.4e}')
                score = 0
                self.agent.sum_loss = 0
                self.agent.sum_entropy = 0


        self.agent.save_model()
        return losses

    def init_wandb (self, project_name, chkpt, resume=False):
        config={
                "name": f"{project_name} {self.chkpt}",
                "device": str(self.agent.policy.device),
                "policy_model":str(self.agent.policy), 
                 "gamma":self.agent.gamma, 
                 "lr":self.agent.policy.lr, 
                 "entropy_coe": self.agent.entropy_coe
                #  "optim_step":self.agent.optim_step, 
                #  "optim_gamma":self.agent.optim_gamma,
                #  'entropy_decay': self.agent.entropy_decay,
                #  'entropy_decay_steps': self.agent.entropy_decay_steps, 
                #  "entropy_coefficient":self.agent.entropy_coefficient, 
                #  'entropy_coe_min':self.agent.entropy_coe_min,
            }
        wandb.init(
            project=project_name,
            resume=resume,
            id=f'{project_name} {chkpt}',
            config=config,
        )

    def log_wandb(self, **kwargs):
        wandb.log(kwargs)


if __name__ == '__main__':
    torch.save(0, 'Data/chkpt')
    chkpt = torch.load('Data/chkpt')
    chkpt+=1
    torch.save(chkpt, 'Data/chkpt')
    trainer = REINFORCE_Trainer(chkpt=chkpt)
    trainer.train(epochs=5000000)
    
            