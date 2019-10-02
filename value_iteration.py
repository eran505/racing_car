import numpy as np
from itertools import product
from itertools import product
from graph_policy import short_path_policy
from planner import construct_map_state
import util_system
import state
from action import action_drive
class value_iteration_object:

    def __init__(self,grid):
        self.start_state=state.game_state(grid)
        self.matrix_v={}
        self.action_map =None
        self.ctr_state=0
        self.map_state={}
        self.state_absorbed_map = None
        self.players= ['B1','A1']
        self.transition_prob=0.9
        self.action_wind = (0,0)
        self.discount_factor=float(0.8)
        self.epsilon = 0.0001
        self.update_state=[]
        self.is_update=True
        self.op_policy=None
        self.transaction_action=None
        self.sum_tran_p=None


    def constractor(self):
        self.transaction_action=np.zeros(len(self.action_map))
        self.transaction_action[self.action_map[(0,0)]]=0.1
        self.sum_tran_p = np.sum(self.transaction_action)

    def get_action(self,state,id_agent,policy_eval):
        a = self.greedy_action(state,id_agent)
        #return [0,0]
        return a

    def greedy_action(self,state,id_agent):
        a_obl = action_drive(None,state)
        d={}
        state_reward, d_action, d_wall = a_obl.get_expected_reward(id_agent)
        for action_i in d_action:
            state_i = d_action[action_i]
            if d_wall[state_i] is True:
                continue
            entry_i =self.map_state[state_i]
            v_i = self.matrix_v[entry_i]
            d[action_i]=v_i
        return action_drive.keywithmaxval(d)

    def rest(self,action=None):
        if self.is_update:
            self.op_policy=action.tran['A1']
            self.loop_update()
        self.is_update=False

    def expected_value_op(self,l_action,str_state):
        v_vector = np.zeros((len(l_action)))
        p_vector = np.zeros((len(l_action)))
        ctr=0
        for a in l_action:
            s_i = util_system.string_change_by_action_id(a[0], 'A1', str_state)
            v = self.matrix_v[self.map_state[s_i]]
            v_vector[ctr]=v*self.discount_factor
            p_vector[ctr]=a[1]
            ctr+=1
        return np.dot(v_vector,p_vector)
    def get_tran(self):
        pass

    def update_table(self):
        '''
        V*(s) = max_a sigma{ T(s,a,s')[R(s,a,s')+discount_factor*V*(s')]}
        thsigma beacuse the probabilty of taking the max a action can lead us to diffrent state,
        we want the expecation of this number
        '''
        i=0
        print ("update_table....")
        error=0
        for ky in self.update_state:
            #print (i)
            i += 1
            entry = self.map_state[ky]
            v = self.matrix_v[entry]
            d_action={}

            vector = np.zeros((len(self.action_map)))
            for action_i in self.action_map:
                d_help={}
                action_entry_i = self.action_map[action_i]
                d_action[action_i]=[]
                state_next = util_system.string_change_by_action_id(action_i,'B1',ky)
                if state_next not in self.map_state:
                    r=self.start_state.wall_reward
                    state_next=util_system.string_change_by_zero_speed('B1',ky)
                if state_next not in d_help:
                    op_pos,op_speed= util_system.get_spped_pos(state_next,'A1')
                    l_action = short_path_policy.optional_next_action(self.op_policy, op_pos, op_speed)
                    v_expected = self.expected_value_op(l_action ,state_next)
                    v_expected += r
                    d_help[state_next] = v_expected
                else:
                    v_expected = d_help[state_next]

                vector[action_entry_i] = v_expected
            d_expected_value={}

            for ky in d_action:
                action_entry = self.action_map[ky]
                self.transaction_action[action_entry] += (1.0 - self.sum_tran_p)

                d_expected_value[ky] = np.round(np.dot(vector, self.transaction_action), 6)

                self.transaction_action[action_entry] -= (1.0 - self.sum_tran_p)

            max_value = util_system.get_max_value_dict(d_expected_value)
            error +=abs(v-max_value)
            #print("error\t",)
            self.matrix_v[entry]=max_value
        return error

    def loop_update(self,max_update = 100):
        ctr=0
        for i in range(100):
            error = self.update_table()
            print(ctr)
            print(error)
            if error < 1:
                break
            ctr+=1
        print ("done")




    def init_matrix(self,x,y,num_agents,action_size=9,speed_state=25,dead_state=1,max_b=30):
            state_size_overall = pow(((x*y)+dead_state)*speed_state*max_b,num_agents)
            self.matrix_v = np.zeros(state_size_overall)
            self.action_map = \
                {(0, 0): 0, (0, 1): 1, (0, -1): 2, (1, 0): 3
                    , (1, 1): 4, (1, -1): 5, (-1, 0): 6, (-1, 1): 7, (-1, -1): 8}
            self.constractor()
    def init_dict_state(self,x,y,max_speed=2,num_players=2):
        self.init_matrix(x,y,num_players)
        self.map_state= construct_map_state(x,y,max_speed,num_players,self.players)
        self.state_absorbed()

    def state_absorbed(self):
        d_all={}
        for state_i in self.map_state:
            obj_state = state.game_state.string_to_state(state_i,self.start_state.grid)
            if obj_state.check_gaol() is not None:
                entry = self.map_state[state_i]
                self.matrix_v[entry]=obj_state.goal_reward
                d_all[entry]=True
            elif obj_state.collusion() is not None:
                entry = self.map_state[state_i]
                self.matrix_v[entry]=obj_state.coll_reward
                d_all[entry] = True
            else:
                self.update_state.append(state_i)

        self.state_absorbed_map=d_all

if __name__ == "__main__":
    pass
