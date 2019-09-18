import copy
import util_system
from agnets import agent_player
from bord_game import grid_puzzle
from state import game_state
from planner import reward_func
import graph_policy as gp
import value_iteration
import time
from math import sqrt,ceil

import pandas as pd
import numpy as np

class system_game:

    def __init__(self):
        self.grid_bord=None
        self.agents_list=None
        self.agents={}
        self.history=[]
        self.agents_out=[]
        self.agents_in={}
        self.current_state=None
        self.previous_state=None



    def set_starting_state(self):
        state_s = game_state()
        for symbol_team in self.agents:
            for agnet_i in self.agents[symbol_team]:
                id_agent = agnet_i.get_id()
                state_s.set_agent_position(id_agent ,agnet_i.starting_point)
                state_s.set_agent_speed(id_agent,(0,0))
                state_s.set_agent_budget(id_agent,agnet_i.budget)
        print (state_s)
        self.current_state = state_s
        self.current_state.grid=self.grid_bord
        self.previous_state = None



    def init_game(self,string_in):
        dico_setting = util_system.stdin_str_to_dict(string_in)
        # puzzle info
        x_size = dico_setting['x']
        y_size = dico_setting['y']
        goalz = dico_setting['G']
        # agent info
        aganet_info_A =  dico_setting['A']
        aganet_info_B = dico_setting['B']
        # staring point
        start_B = dico_setting['B_s']
        start_A = dico_setting['A_s']

        # set players
        self.set_agents(aganet_info_B,start_B,'B')
        self.set_agents(aganet_info_A, start_A, 'A')

        #set grid
        bord = grid_puzzle('grid',int(x_size),int(y_size))
        goals_coords = util_system.str_to_point(goalz)
        for item in goals_coords:
            bord.set_gaol(item)
        self.grid_bord = bord

        # set point on the grid
        self.set_starting_point_grid()

        # rest all agents
        self.agents_in = copy.deepcopy(self.agents)
        self.agents_out = []


        self.set_policies()

        self.set_starting_state()

        #self.update()


        print ('-'*100)

    def set_starting_point_grid(self):
        for t_team in self.agents.keys():
            for agent_i in self.agents[t_team]:
                team_i = agent_i.team
                team_i = str(team_i).lower()
                arr = agent_i.starting_place_list
                for coord in arr:
                    self.grid_bord.set_starting_point(coord,team_i)

    def set_value_itr(self,agent):
        update_num = ceil(sqrt(pow(self.grid_bord.y_size,2)+pow(self.grid_bord.x_size,2)))+1
        print ("update_value:\t{}".format(update_num))
        v = value_iteration.value_iteration_object(self.grid_bord)
        v.init_dict_state(self.grid_bord.x_size,self.grid_bord.y_size)
        v.loop_update(update_num)
        agent.policy_object=v

    def set_policies(self):
        for stymbol in self.agents:
            for agent_i in self.agents[stymbol]:
                if agent_i.policy_name == 'short':
                    self.set_policy_agent_short(agent_i)
                elif agent_i.policy_name == 'random':
                    self.set_policy_agent_random(agent_i)
                elif agent_i.policy_name == 'value':
                    self.set_value_itr(agent_i)
                agent_i.reset_agent()  # rest properties

    def id_to_agents(self,list_id):
        agentz=[]
        for id_i in list_id:
            team=id_i[:-1]
            for p in self.agents[team]:
                if p.name_id == id_i:
                    agentz.append(p)
        return agentz


    def set_policy_agent_random(self,agent):
        agent.init_policy(None, 'random')

    def set_policy_agent_short(self,agent):
        d_path={}
        for goal in self.grid_bord.goals_box:
            for start_p in agent.get_starting_points():
                res = gp.get_short_path_from_grid(self.grid_bord,start_p,goal)
                if start_p not in d_path:
                    d_path[start_p]={}
                d_path[start_p][goal]=res
        agent.init_policy(d_path,'short')



    def set_agents(self,str_setting,start_point,team_name_prffix):
        ctr_agent = 1
        info_array = ' '.join(' '.join(str(str_setting).split('|')).split(':'))
        dico_setting = util_system.stdin_str_to_dict(info_array)
        num_agaent = dico_setting['n']
        policy = dico_setting['p']
        s_budget= dico_setting['b']
        arry_starting_point = start_point.split(':')
        agents_list=[]
        for i in range(int(num_agaent)):
            agent_i = agent_player(name='{}{}'.format(team_name_prffix,ctr_agent),
                                   policy=policy,starting_budget=s_budget,team_symbol=team_name_prffix)
            agent_i.set_staring_point_str(start_point)
            ctr_agent+=1
            agents_list.append(agent_i)
        self.agents[team_name_prffix]=agents_list

    def remove_agent(self,player):
        team = player.get_team()
        self.agents_in[team].remove(player.get_id())
        print(str(player),'|\tremoved')

        self.agents_out.append(player)
        self.current_state.dead_player_position(player.get_id())

    def end_game(self):
        '''
        check if there no player in one of the team
        '''
        d={'A':0,'B':0}
        for team_i in self.agents_in:
            if len(self.agents_in[team_i])==0:
                if team_i == 'B':
                    d['B'] = 1
                elif team_i =='A':
                    d['A'] = 1

        if (d['A']==0 and d['B']==1) or (d['A']==0 and d['B']==0):
            return False
        return True

    def print_state(self):
        self.grid_bord.print_state(self.current_state.player_position,self.current_state.dead_state)


    def check_conditions(self):
        '''
        conditions:
        (1)collusion
        (2)out of budget
        (3)at the goal
        '''

        # check 2
        list_agents_id = self.current_state.budget_checking()
        if list_agents_id is not None:
            to_remove = self.id_to_agents(list_agents_id)
            for p in to_remove:
                self.remove_agent(p)
            print('out of budget!!')
            return True,'budget'

        # check 1
        agentz = self.current_state.collusion()
        if agentz is not None:
            print("agentz: ", agentz)
            for collusion_i in agentz:
                for agent_p in collusion_i:
                    agent_obj = self.id_to_agents([agent_p['p']])[0]

                    reward_func(self.agents_in,agentz,'collusion',self.current_state.coll_reward)

                    self.remove_agent(agent_obj)
            print ('collusion!!')
            return True,'collusion'

        #check 3
        agentz  = self.current_state.check_gaol()
        if agentz is not None:
            print('at the goal!!')
            agents_objects = self.id_to_agents(agentz)
            reward_func(self.agents_in, agentz, 'goal',self.current_state.goal_reward)
            for obj_player in agents_objects :
                self.remove_agent(obj_player)

            self.remove_all_player()

            return True,'goal'

        return False,None


    def remove_all_player(self):
        for team in self.agents_in:
            for p_player in self.agents_in[team]:
                self.remove_agent((p_player))

    def check_valid_move(self):
        pos_list = self.current_state.player_position
        for p in pos_list.keys():
            if self.current_state.dead_state[0] == pos_list[p][0] and self.current_state.dead_state[1] == pos_list[p][1]:
                continue
            if self.grid_bord.is_vaild_move(pos_list[p][0],pos_list[p][1]) is False:
                return False
        return True

    def rollback(self):
        print ('rollback')
        self.current_state.state_rollback_exclude_budget(self.previous_state)


    def check_reward(self):
        pass

    def start_game(self):
        is_end = False
        info=None
        ctr_rounds=0
        while True:
            self.print_state()
            print (self.current_state)
            #print ('\n')
            self.history.append(str(self.current_state))
            for symbol in self.agents_in:
                if is_end:
                    break
                for agent_i in self.agents_in[symbol]:
                    # deep copying the sate for rollback
                    self.previous_state = self.current_state.get_deep_copy_state()

                    agent_i.play(self.current_state)
                    #valid move
                    if self.check_valid_move() is False:
                        reward_func(agent_i,None,'wall',self.current_state.wall_reward)
                        self.rollback()
                    self.check_reward()
                    is_removed,info = self.check_conditions()
                    if is_removed:
                        if self.end_game():
                            is_end=True
                            break

            ctr_rounds+=1
            print ("round : {}".format(ctr_rounds))
            if is_end:
                print ('---End Episode---')
                break

        return info,ctr_rounds

    def start_episode(self):
        self.history=[]
        self.agents_in=copy.deepcopy(self.agents)
        self.agents_out=[]
        for sym in self.agents_in:
            for p in self.agents_in[sym]:
                p.reset_agent()
        self.set_starting_state()

    def loop_game(self,num_of_epsidoe=400):
        d_l=[]
        for i in range(num_of_epsidoe):
            self.start_episode()
            info, ctr_rounds = self.start_game()
            d_l.append({'round':ctr_rounds,'end':info,'history':" / ".join(self.history)})
        df = pd.DataFrame(d_l)
        df['collusion']= np.where(df['end']=='collusion', 1, 0)
        df['goal'] = np.where(df['end'] == 'goal', 1, 0)
        df['budget'] = np.where(df['end'] == 'budget', 1, 0)

        print (df.to_string())
        df.to_csv('{}/{}.csv'.format('/home/ise/car_model',time.strftime("%m_%d_%H_%M_%S")),sep='\t')


if __name__ == "__main__":


    std_in_string = '-x 6 -y 6 -G 0,0:2,0 -A -n|1:-p|short:-b|50 -B -n|1:-p|value:-b|100 -B_s 1,0 -A_s 5,5'
    s = system_game()
    s.init_game(std_in_string)
    s.loop_game()
    std_in_string = '-x 7 -y 7 -G 0,0:2,0 -A -n|1:-p|short:-b|50 -B -n|1:-p|value:-b|100 -B_s 1,0 -A_s 6,6'
    s = system_game()
    s.init_game(std_in_string)
    s.loop_game()

    #print ("system class")
