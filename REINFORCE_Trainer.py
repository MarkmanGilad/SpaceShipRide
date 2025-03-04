import torch
import pygame
from REINFORCE_Agent import REINFORCE_Agent
from Environment import SpaceShipRide
import wandb
from Graphics import *
 

class REINFORCE_Trainer:
    def __init__(self,  chkpt):
        self.agent:REINFORCE_Agent = REINFORCE_Agent(chkpt=chkpt)
        self.env:SpaceShipRide = SpaceShipRide()
        self.chkpt = chkpt

    def train(self, epochs=100000):
        self.init_wandb(project_name="REINFORCE-continuous",chkpt=self.chkpt,resume=False)
        wins = 0
        for epoch in range(epochs):
            self.env.restart()
            self.env.step = 0
            score = 0
            self.env.done = False
            ########### sample environment ###########
            while not self.env.done:
                self.env.step += 1
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                pygame.event.pump()
                state = self.env.get_state()
                action, action_tensor = self.agent.get_action(state, train=True)
                self.env.render(action)
                reward = self.env.get_reward()
                
                #reward2 += reward1
                self.agent.remember(state, action_tensor, reward)
                score += reward

            
            ########### train ###########
            # print (f"\nstep: {self.env.step} reward: {self.env.get_reward()} ")
            self.agent.learn()

            ########### log ###########
            wins += int(self.env.win)
            if epoch % 1 ==0 :
                s = self.env.step
                self.log_wandb(score=score, loss = self.agent.sum_loss/s, entropy = self.agent.sum_entropy/s)
                print ( f'chkpt: {self.chkpt} epoch: {epoch} step: {self.env.step} wins: {wins} score: {score} loss: {self.agent.sum_loss/s}',
                        f'entropy: {self.agent.sum_entropy/s} action_tensor: {action_tensor} action {action}')
                self.agent.sum_loss = 0
                self.agent.sum_entropy = 0
                if epoch %  100 == 0:
                    self.log_wandb(wins=wins)
                    wins = 0    

                    


        self.agent.save_model()
        

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
    try:
        chkpt = torch.load('Data/chkpt')
    except:
        chkpt = 0
    chkpt+=1
    torch.save(chkpt, 'Data/chkpt')
    trainer = REINFORCE_Trainer(chkpt=chkpt)
    trainer.train(epochs=1000000)
    