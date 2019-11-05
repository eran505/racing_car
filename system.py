import copy
import util_system
from agnets import agent_player
from bord_game import grid_puzzle
from state import game_state
from planner import reward_func
import graph_policy as gp
import value_iteration
import time
import os
from math import sqrt,ceil
import rtdp_algo
import pandas as pd
import numpy as np
from action import action_drive
class system_game:

    def __init__(self):
        self.grid_bord=None
        self.agents_list=None
        self.agents={}
        self.action_drive_object=action_drive(None,None)
        self.history=[]
        self.agents_out={}
        self.agents_in={}
        self.current_state=None
        self.previous_state=None
        self.stop_arr=[]



    def set_starting_state(self):
        state_s = game_state()
        for symbol_team in self.agents_in:
            for agnet_i in self.agents_in[symbol_team]:
                id_agent = agnet_i.get_id()
                state_s.set_agent_position(id_agent ,agnet_i.starting_point)
                state_s.set_agent_speed(id_agent,(0,0))
                state_s.set_agent_budget(id_agent,agnet_i.budget)
                #self.action_drive_object.set_tran(id_agent,agnet_i.policy_object.get_tran())
        #print (state_s)
        self.current_state = state_s
        self.current_state.grid=self.grid_bord
        self.action_drive_object.set_state(self.current_state)
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

        self.agents_in=self.agents

        #set grid
        bord = grid_puzzle('grid',int(x_size),int(y_size))
        goals_coords = util_system.str_to_point(goalz)
        for item in goals_coords:
            bord.set_gaol(item)
        self.grid_bord = bord

        # set point on the grid
        self.set_starting_point_grid()




        self.set_policies()

        self.set_starting_state()

        #self.update()


        # rest all agents
        #self.agents_in = copy.deepcopy(self.agents)
        #self.agents_in = self.agents

        self.agents_out = {'A':[],'B':[]}

        self.copy_agents(self.agents_in,self.agents_out)
        self.agents_in = {'A': [], 'B': []}
        #print ('-'*100)

    def get_max_speed_from_all_players(self):
        arr=[]
        for team_index in self.agents:
            for p in self.agents[team_index]:
                arr.append(p.get_max_speed())
        return arr

    def set_rtdp(self,agent):
        arr_max_speed=self.get_max_speed_from_all_players()
        rtdp_obj = rtdp_algo.rtdp(self.grid_bord,agent.get_max_speed())
        rtdp_obj.init_policy(self.grid_bord.x_size,self.grid_bord.y_size,arr_max_speed)
        agent.policy_object=rtdp_obj


    def copy_agents(self,l_copy,l_dis):
        for sym in l_copy:
            for p in l_copy[sym ]:
                l_dis[sym].append(p)


    def set_starting_point_grid(self):
        for t_team in self.agents_in.keys():
            for agent_i in self.agents_in[t_team]:
                team_i = agent_i.team
                team_i = str(team_i).lower()
                arr = agent_i.starting_place_list
                for coord in arr:
                    self.grid_bord.set_starting_point(coord,team_i)

    def set_value_itr(self,agent):
        update_num = ceil(sqrt(pow(self.grid_bord.y_size,2)+pow(self.grid_bord.x_size,2)))+1
        update_num = 15

        v = value_iteration.value_iteration_object(self.grid_bord)
        v.init_dict_state(self.grid_bord.x_size,self.grid_bord.y_size)
        agent.policy_object = v

    def set_policies(self):
        for stymbol in self.agents:
            for agent_i in self.agents[stymbol]:
                if agent_i.policy_name == 'short':
                    self.set_policy_agent_short(agent_i)
                elif agent_i.policy_name == 'random':
                    self.set_policy_agent_random(agent_i)
                elif agent_i.policy_name == 'value':
                    self.set_value_itr(agent_i)
                elif agent_i.policy_name == 'dog':
                    agent_i.init_policy(None,'dog')
                elif agent_i.policy_name == 'rtdp':
                    self.set_rtdp(agent_i)

                self.action_drive_object.set_tran(agent_i.get_id(), agent_i.policy_object.get_tran())

        for stymbol in self.agents:
            for agent_i in self.agents[stymbol]:
                agent_i.reset_agent(self.action_drive_object)  # rest properties

    def id_to_agents(self,list_id):
        agentz=[]
        for id_i in list_id:
            team=id_i[:-1]
            for p in self.agents_in[team]:
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
        agent.init_policy(d_path,'short',agent.max_speed)



    def set_agents(self,str_setting,start_point,team_name_prffix):
        ctr_agent = 1
        info_array = ' '.join(' '.join(str(str_setting).split('|')).split(':'))
        dico_setting = util_system.stdin_str_to_dict(info_array)
        num_agaent = dico_setting['n']
        policy = dico_setting['p']
        max_speed_move = int(dico_setting['m'])
        s_budget= dico_setting['b']
        arry_starting_point = start_point.split(':')
        agents_list=[]
        for i in range(int(num_agaent)):
            agent_i = agent_player(name='{}{}'.format(team_name_prffix,ctr_agent),
                                   policy=policy,starting_budget=s_budget,team_symbol=team_name_prffix)
            agent_i.set_staring_point_str(start_point)
            agent_i.set_max_speed(max_speed_move)
            self.action_drive_object.set_max_speed(agent_i.get_id(),max_speed_move)
            ctr_agent+=1
            agents_list.append(agent_i)
        self.agents[team_name_prffix]=agents_list

    def remove_agent(self,player):
        team = player.get_team()
        self.agents_in[team].remove(player.get_id())
        #print(str(player),'|\tremoved')
        self.agents_out[player.get_team()].append(player)
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
        (4) wall optional
        '''
        list_to_remove=[]

        # wall

        players_wall =  self.current_state.is_wall_state()
        if players_wall is not None:
            to_remove = self.id_to_agents(players_wall)
            for p in to_remove:
                list_to_remove.append(p)
            #print ('Wall')
            return True,'Wall',0,list_to_remove,True


        # check 2
        list_agents_id = self.current_state.budget_checking()
        if list_agents_id is not None:
            to_remove = self.id_to_agents(list_agents_id)
            for p in to_remove:
                list_to_remove.append(p)
            #print('out of budget!!')
            return True,'budget',0,list_to_remove,True


        #check 3
        agentz  = self.current_state.check_gaol()
        if agentz is not None:
            #print('at the goal!!')
            agents_objects = self.id_to_agents(agentz)
            reward_func(self.agents_in, agentz, 'goal',self.current_state.goal_reward)
            for obj_player in self.agents_in['A']:
                list_to_remove.append(obj_player)
            for obj_player in self.agents_in['B']:
                obj_player.reward+=self.current_state.goal_reward
                list_to_remove.append(obj_player)


            return True,'goal',self.current_state.goal_reward,list_to_remove,True


        # check 1
        agentz = self.current_state.collusion()
        if agentz is not None:
            #print("agentz: ", agentz)
            for collusion_i in agentz:
                for agent_p in collusion_i:
                    agent_obj = self.id_to_agents([agent_p['p']])[0]
                    agent_obj.reward+=self.current_state.coll_reward
                    list_to_remove.append(agent_obj)

            #print ('collusion!!')
            return True,'collusion',self.current_state.coll_reward,list_to_remove,True



        return False,None,0,list_to_remove,False


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
        #print ('rollback')
        self.current_state.state_rollback_exclude_budget(self.previous_state)

    def remove_players_list(self,l_to_remove):
        for p in l_to_remove:
            self.remove_agent(p)

    def update_policy(self,player,s_old,r,a,s_new):
        player.update(s_old,r,a,s_new,self.action_drive_object)


    def start_game(self,policy_eval):

        is_end = False
        info=None
        ctr_rounds=0

        while True:
            sum_of_reward=0
            #print ('\n')
            #self.history.append(str(self.current_state))
            for symbol in self.agents_in:

                if is_end:
                    break
                for agent_i in self.agents_in[symbol]:
                    # deep copying the sate for rollback
                    self.previous_state = self.current_state.get_deep_copy_state()

                    a = agent_i.play(self.current_state,policy_eval,self.action_drive_object)
                    #print (str(agent_i),"\tAction=",a)
                    #self.print_state()
                    #print(self.current_state)

                    is_removed,info,r,l_remove,fin_state = self.check_conditions()
                    #print (info)
                    #self.update_policy(agent_i, self.previous_state, r, a, self.current_state)

                    if is_removed:
                        for player_i in l_remove:
                            if player_i.get_team()=='B':

                                sum_of_reward+=player_i.reward
                            self.remove_agent(player_i) # remove player


                    # end loop
                    if is_removed:
                        #if self.end_game() :
                        is_end=True
                        #self.history.append(str(self.current_state))
                        break

            ctr_rounds+=1
            #print ("round : {}".format(ctr_rounds))
            if is_end:
                #print ('---End Episode---')
                break


        #print (sum_of_reward)
        return info,ctr_rounds,sum_of_reward

    def start_episode(self):
        self.history=[]
        self.copy_agents(self.agents_out,self.agents_in)
        self.agents_out={'A':[],'B':[]}


        for p in self.agents_in['B']:
            p.reset_agent(info=self.action_drive_object)

        for p in self.agents_in['A']:
            p.reset_agent(info=self.action_drive_object)

        self.set_starting_state()

    def loop_game(self,n,num_of_epsidoe=7000,info_string='_'):
        d_list=[]
        num_of_epsidoe = num_of_epsidoe + 1
        for i in range(1,num_of_epsidoe):
            if i%1000==0:
                print (i)
                sum_col,wall_sum, sum_goal, avg_round, r = self.eval_policy()
                d_list.append({'iter': i,'Avg Rerward':r ,'wall_sum':wall_sum,'sum_collusion':sum_col, 'sum_goal':sum_goal,'avg_round':avg_round})
                self.start_episode()
                if self.is_stop(i):
                    break
            self.start_episode()
            info, ctr_rounds,r = self.start_game(policy_eval=False)
            #print ('num_of_epsidoe:\t',i)
        time_now=time.strftime("%m_%d_%H_%M_%S")
        name_file = 'N_{}_T_{}_info_{}'.format(n,time_now,info_string)
        print (self.print_policy(name_file))
        df_fin =pd.DataFrame(d_list)
        df_fin.to_csv('{}/{}.csv'.format('/home/ise/car_model',name_file), sep='\t')

    def eval_policy(self, num_of_iteration=400):
        d_l = {'collusion': 0,'Wall':0, 'goal': 0, 'round': [], 'reward': []}

        for i in range(num_of_iteration):
            self.start_episode()
            info, ctr_rounds, r = self.start_game(policy_eval=True)
            d_l['round'].append(ctr_rounds)
            d_l['reward'].append(r)
            if info == 'collusion':
                d_l['collusion'] += 1
            elif info == 'Wall':
                d_l['Wall'] += 1
            else:
                d_l['goal'] += 1

        avg_reward = sum(d_l['reward']) / float(len(d_l['reward']))
        print ('avg_reward :\t',avg_reward)
        avg_round = sum(d_l['round']) / float(len(d_l['round']))

        #self.print_policy()

        return d_l['collusion'],d_l['Wall'] ,d_l['goal'], avg_round, avg_reward

    def print_policy(self,name):
        to_file_dist = '{}/{}/{}'.format('/home/ise/car_model','data',name)
        for sym in self.agents_in:
            for p in self.agents_out[sym]:
                str_info_policy = p.policy_object.policy_data(to_file_dist)
                to_disk(str_info_policy)
                print (str_info_policy)

    def is_stop(self,i):
        if i>=1000000:
            return True
        acc=0
        for p in self.agents['B']:
            ctr_state_up_date = p.policy_object.ctr_state
            acc+=ctr_state_up_date
        self.stop_arr.append(acc)
        #print (self.stop_arr)
        if len(self.stop_arr) == 4:
            if len(set(self.stop_arr)) == 1:
                #print('innn')
                return True
            self.stop_arr=[]
        return False

def to_disk(msg,path_file='/home/ise/car_model/info.txt'):
    if os.path.isfile(path_file) is False:
        os.system('touch {}'.format(path_file))
    with open(path_file, "a") as myfile:
        myfile.write(msg+'\n')




def generator_game():

    for item in range(12,22):
        speed_A=2
        speed_B=1
        #goal_one,goal_two = np.random.choice(item,2,False)
        goal_one, goal_two=2,0
        iter_num = item * 3000
        if item>=10:
            speed_A+=1
            speed_B+=1
            iter_num=iter_num*10
        if item>15:
            iter_num = iter_num*10
            speed_A+=2
            speed_B+=1

        str_i='-x {0} -y {0} -G {4},0:{5},0 -A -n|1:-p|short:-b|52:-m|{2} -B -n|1:-p|rtdp:-b|100:-m|{3} -B_s 1,0 -A_s {1},{1}'.format(item,item-1,speed_A,speed_B,
                                                                                                                                    goal_one,goal_two)

        print (str_i)
        to_disk(str_i)
        s = system_game()
        s.init_game(str_i)
        s.loop_game(item,iter_num,'G_{}_{}'.format(goal_one,goal_two))

        str_i='-x {0} -y {0} -G {4},0:{5},0 -A -n|1:-p|short:-b|52:-m|{2} -B -n|1:-p|dog:-b|100:-m|{3} -B_s 1,0 -A_s {1},{1}'.format(item,item-1,speed_A,speed_B,
                                                                                                                                    goal_one,goal_two)

        #print (str_i)
        #to_disk(str_i)
        #s = system_game()
        #s.init_game(str_i)
        #s.loop_game(item)



#import cProfile
import time
from queue import Queue
if __name__ == "__main__":


    generator_game()
    exit()
    #std_in_string = '-x 9 -y 9 -G 7,0 -A -n|1:-p|short:-b|52:-m|1 -B -n|1:-p|rtdp:-b|100:-m|1 -B_s 0,1 -A_s 8,8'
    #std_in_string = '-x 8 -y 8 -G 0,0:5,0 -A -n|1:-p|short:-b|50:-m|2 -B -n|1:-p|rtdp:-b|100:-m|1 -B_s 1,0 -A_s 7,7'
    #std_in_string = '-x 7 -y 7 -G 0,0 -A -n|1:-p|short:-b|50:-m|2 -B -n|1:-p|rtdp:-b|100:-m|1 -B_s 2,0 -A_s 6,6'
    #std_in_string = '-x 4 -y 4 -G 0,0 -A -n|1:-p|short:-b|50 -B -n|1:-p|rtdp:-b|100 -B_s 3,0 -A_s 3,3'
    #std_in_string = '-x 3 -y 3 -G 0,0 -A -n|1:-p|short:-b|50:-m|1 -B -n|1:-p|rtdp:-b|100:-m|1 -B_s 2,0 -A_s 2,2'
    #std_in_string = '-x 5 -y 5 -G 0,0 -A -n|1:-p|short:-b|50:-m|1 -B -n|1:-p|rtdp:-b|100:-m|1 -B_s 2,0 -A_s 4,4'
    #std_in_string = '-x 4 -y 4 -G 2,0 -A -n|1:-p|short:-b|10:-m|1 -B -n|1:-p|rtdp:-b|10:-m|1 -B_s 2,0 -A_s 3,3'
    #std_in_string = '-x 6 -y 6 -G 0,0  -A -n|1:-p|short:-b|52:-m|1 -B -n|1:-p|rtdp:-b|100:-m|1 -B_s 1,0 -A_s 5,5'
    #std_in_string='-x 11 -y 11 -G 3,0:4,0 -A -n|1:-p|short:-b|52:-m|3 -B -n|1:-p|rtdp:-b|100:-m|2 -B_s 1,0 -A_s 10,10'
    std_in_string = '-x 5 -y 5 -G 0,0 -A -n|1:-p|short:-b|50:-m|1 -B -n|1:-p|rtdp:-b|100:-m|1 -B_s 2,0 -A_s 4,4'
    #std_in_string = '-x 8 -y 8 -G 6,0:0,0 -A -n|1:-p|short:-b|50:-m|1 -B -n|1:-p|rtdp:-b|100:-m|1 -B_s 6,0 -A_s 7,7'

    s = system_game()
    s.init_game(std_in_string)
    s.loop_game(9, 1000)


    exit()
    #cProfile.runctx("s.loop_game(11,5000)", globals(), locals())
    #print ("system class")
