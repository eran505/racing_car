
from time import time
from planner import init_dict_state_helper,construct_map_state
import numpy as np
import state
from action import action_drive
class rtdp:

    def __init__(self,grid):
        self.name='RTDP'
        self.matrix_q=None
        self.players = ['A1','B1']
        self.num_of_epsiode=None
        self.state_absorbed_map=None
        self.action_object=None
        self.discounted_factor=0.8
        self.ctr_insert_state=0
        self.grid=grid
        self.map_state=None
        self.heuristic_value_upper_bound = 10.0
        self.transaction_action=None
        self.action_map=None
        self.sum_tran_p=None
        self.size_action=-1
        self.transitions=None
        self.init_action_map()

    def init_action_map(self):
        self.action_map =\
            {(0,0): 0, (0,1): 1, (0,-1): 2, (1,0): 3
            , (1,1): 4, (1,-1): 5, (-1,0): 6, (-1,1): 7, (-1,-1): 8}
        self.transaction_action=np.zeros(len(self.action_map))
        self.transaction_action[self.action_map[(0,0)]]=0.1
        self.sum_tran_p = np.sum(self.transaction_action)
        self.size_action = len(self.action_map)


    def full_init(self,x,y,num_agents,max_speed,full,max_b=1):
        speed_state = pow((abs(max_speed)*2)+1,2)
        state_size_overall = pow(((x * y) + 1) * speed_state * max_b, num_agents)
        print ("state_size_overall: ",state_size_overall )
        if full is False:
            self.matrix_q = np.full((state_size_overall, len(self.action_map)), self.heuristic_value_upper_bound)
        else:
            self.matrix_q = np.full((state_size_overall, len(self.action_map)),self.heuristic_value_upper_bound)
            self.map_state= construct_map_state(x,y,max_speed,num_agents,self.players)
            self.state_absorbed()
        print ('done')



    def init_policy(self,x,y,max_speed=2,player_number=2,full=True):
        self.full_init(x,y,player_number,max_speed,full)



    def rest(self,obj):
        pass
    def get_tran(self):
        return None

    def up_date_q_observing(self,string_i,reward):
        for state_i in self.state_absorbed_map[string_i]:
            entry_q = self.map_state[state_i]
            self.matrix_q[entry_q,:]=reward




    def state_absorbed(self):
        d_goal={}
        d_coll={}
        obj_state=None
        for state_i in self.map_state:
            obj_state = state.game_state.string_to_state(state_i,self.grid)
            if obj_state.check_gaol() is not None:
                d_goal[state_i]=True
            elif obj_state.collusion() is not None:
                d_coll[state_i] = True
        self.state_absorbed_map={'goal':d_goal,'collusion':d_coll}
        self.up_date_q_observing('goal',obj_state.goal_reward)
        self.up_date_q_observing('collusion', obj_state.coll_reward)


    def get_action(self,state,player_id,policy_eval,action_object):
        action_a = action_object
        state_reward, d_action, d_wall = action_a.get_expected_reward(player_id)
        a = self.greedy_action_taking(state,state_reward, d_action, d_wall,policy_eval)
        print("a= ",a)
        return a

    def greedy_action_taking(self, state_cur, state_reward ,d_action, d_wall,policy_eval):
        '''
        Q(S,A) = R(S,A)+ discount*T(S'|S,A)*V(S')
        V(S)=max_a{Q(S,A)}
        '''

        state_old_str = state_cur.state_to_string_no_budget()
        entry_q = self.map_state[state_old_str]
        d_expected_value={}
        vector = np.zeros((self.size_action))
        for action_a in d_action:
            action_entry = self.action_map[action_a]
            state_s = d_action[action_a]
            if d_wall[state_s]:
                q_value = state_cur.wall_reward
            else:
                next_state_entry = self.map_state[state_s]
                q_value = np.amax(self.matrix_q[next_state_entry, :])

            # elif state_s in self.state_absorbed_map['goal']:
            #     #vector[action_entry]= state_cur.goal_reward
            #     r=state_cur.goal_reward
            #     next_state_entry = self.map_state[state_s]
            #     q_value = np.amax(self.matrix_q[next_state_entry, :])
            #     #self.update_q(action_entry, entry_q, q_value*self.discounted_factor )
            # elif state_s in self.state_absorbed_map['collusion']:
            #     #vector[action_entry] = state_cur.coll_reward
            #     r=state_cur.coll_reward
            #     next_state_entry = self.map_state[state_s]
            #     q_value = np.amax(self.matrix_q[next_state_entry, :])
            #     #self.update_q(action_entry, entry_q, q_value*self.discounted_factor )
            # else:
            #     next_state_entry = self.map_state[state_s]
            #     q_value = np.amax(self.matrix_q[next_state_entry,:])


            if state_reward[state_s] != 0 :
                vector[action_entry] =  state_reward[state_s]
            else:
                vector[action_entry] = q_value * self.discounted_factor + state_reward[state_s]

        for ky in d_action:
            action_entry = self.action_map[ky]
            self.transaction_action[action_entry]+=(1.0-self.sum_tran_p)
            d_expected_value[ky]=np.dot(vector,self.transaction_action)
            self.transaction_action[action_entry] -= (1.0 - self.sum_tran_p)
        arg_max_action = action_drive.keywithmaxval(d_expected_value)

        # updating the Q table
        if policy_eval is False:
            print(self.matrix_q[entry_q, :])
            self.update_q(self.action_map[arg_max_action],entry_q,d_expected_value[arg_max_action])
            print (self.matrix_q[entry_q,:])

        return arg_max_action


    def update_q(self,action_entry,state_entry,q_new_val):
        self.matrix_q[state_entry,action_entry]= q_new_val



if __name__ == "__main__":
    print ('RTDP')


    arr2D = np.array(   [[11, 12, 13],
                         [14, 15, 16],
                         [17, 15, 11],
                         [12, 14, 15]])

    print ( np.amax(arr2D[1,:]))