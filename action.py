from graph_policy import short_path_policy
from random import choices,choice
import copy
class action_drive:

    def __init__(self,speed,state):
        self.speed_to_add=speed
        self.cur_state = state
        self.step_cost=0.01
        self.cost=0.5
        self.absolute_max_speed=2
        self.action_list = [(0,0),(0,1),(0,-1),(1,1),(1,0),(1,-1),(-1,-1),(-1,1),(-1,0)]
        self.tran={}
        self.wall=None

    def set_tran(self,id_p,tran):
        self.tran[id_p]=tran

    def setter(self,speed,state):
        self.cur_state=state
        self.speed_to_add=speed

    def set_state(self,state):
        self.cur_state=state

    def execute_action(self,id_p):
        self.stochastic_action(id_p)
        r = self.apply_action(id_p)
        return r
    def stochastic_action(self,player_id):
        if str(player_id).__contains__('B'):
            d={}
            for k in self.action_list:
                d[k]=0
                if k == tuple(self.speed_to_add):
                    d[k]+=0.9
                if k == (0,0):
                    d[k]+=0.1
            population = list(d.keys())
            weights = list(d.values())
            a = choices(population, weights)
            self.speed_to_add=a[0]

    def cost_function(self):
        pass

    def apply_action(self,agent_id):
        r=0
        new_speed = self.change_speed(agent_id)
        pos_cur = self.cur_state.get_agent_position(agent_id)
        old_pos = copy.deepcopy(pos_cur)
        new_pos = [pos_cur[i] + new_speed[i] for i in range(len(new_speed))]
        budget_cur = self.cur_state.get_agent_budget(agent_id)
        self.cur_state.set_agent_budget(agent_id,budget_cur - self.cost)

        if self.out_of_bound(new_pos):
            self.cur_state.set_agent_position(agent_id, old_pos)
            self.cur_state.set_agent_speed(agent_id, (0,0))
            self.wall = True
            r+=self.cur_state.wall_reward
        else:
            self.cur_state.set_agent_position(agent_id,new_pos)
            self.wall=False

        r+=self.step_cost

        return r

    def out_of_bound(self,new_pos):
        if self.cur_state.grid.is_vaild_move(new_pos[0],new_pos[1]):
            return False
        return True


    def change_speed(self,agent_id):
        old_speed = self.cur_state.get_agent_speed(agent_id)
        new_speed = [self.speed_to_add[i] + old_speed[i] for i in range(len(old_speed))]
        self.cur_state.set_agent_speed(agent_id,new_speed)
        new_speed = self.check_limit_speed(new_speed)
        return new_speed

    def check_limit_speed(self,speed):
        for i in range(len(speed)):
            if abs(speed[i]) > self.absolute_max_speed:
                if speed[i]>0:
                    speed[i]=self.absolute_max_speed
                else:
                    speed[i] = self.absolute_max_speed*(-1)
        return speed


    def get_max_action(self):
        pass

    def expected_return_reward(self,state):
        self.cur_state=state
        state_next_states = self.all_tran_function()
        return state_next_states

    def get_next_state(self,player_id,action_set):
        s_state = self.cur_state.get_deep_copy_state()
        d_all={}
        for action_a in action_set:
            self.speed_to_add=action_a
            self.cur_state = s_state.get_deep_copy_state()
            self.apply_action(player_id)
            r = self.step_cost
            r += self.cur_state.get_reward_by_state()
            if r == self.step_cost:
                if self.wall is True:
                    r += self.cur_state.wall_reward
                self.tran_function()
                r += self.cur_state.get_reward_by_state()
                r += self.step_cost
            str_state=self.cur_state.state_to_string_no_budget()
            d_all[action_a]=(str_state,r)

        return d_all


    def get_expected_reward(self,player_id):
        s_state = self.cur_state.get_deep_copy_state()
        #action_list = [(0,0),(0,1),(0,-1),(1,1),(1,0),(1,-1),(-1,-1),(-1,1),(-1,0)]
        d_all={}
        for action_a in self.action_list:
            self.speed_to_add=action_a
            self.cur_state = s_state.get_deep_copy_state()
            self.apply_action(player_id)
            r = self.step_cost
            reward = self.cur_state.get_reward_by_state()
            if reward == 0:
                if self.wall is True:
                    r += self.cur_state.wall_reward
                l_str_states = self.tran_function()
                #r += self.step_cost
                d_all[action_a] = (l_str_states, float(r))
            else:
                str_state=self.cur_state.state_to_string_no_budget()
                d_all[action_a]=([(str_state,1.0)],float(r))
        return d_all


    def tran_function(self,id_roll='A1',expected=False):
        list_a = short_path_policy.get_expected_action(self.cur_state,id_roll,self.tran[id_roll])
        list_state = []
        state_old = self.cur_state.get_deep_copy_state()
        for item in list_a:
            a = item[0]
            self.cur_state = state_old.get_deep_copy_state()
            self.speed_to_add=a
            self.apply_action(id_roll)
            str_state = self.cur_state.state_to_string_no_budget()
            list_state.append( (str_state, item[1]) )
        return list_state

    def all_tran_function(self,id_roll='A1'):
        a = short_path_policy.policy_next_step_shortest_path \
            (self.tran[id_roll], self.cur_state.get_agent_position(id_roll), self.cur_state.get_agent_speed(id_roll))
        self.speed_to_add = a
        self.apply_action(id_roll)
        return [(1.0,self.cur_state.state_to_string_no_budget())]


    @staticmethod
    def keywithmaxval(d):
        """ a) create a list of the dict's keys and values;
            b) return the key with the max value"""
        v = list(d.values())
        k = list(d.keys())
        l=[k[0]]
        size = len(k)
        v_max=v[0]
        for i in range(1,size):
            if v_max<v[i]:
                l=[k[i]]
                v_max=v[i]
            elif v_max==v[i]:
                l.append(k[i])
        res = choice(l)
        return res


if __name__ == "__main__":
    d={}
    d[(0, 0)] = 4
    d[(1, 0)] = 2
    d[(2, 0)] = 3
    d[(3, 0)] = 5
    d[(4, 0)] = 5
    x= action_drive.keywithmaxval(d)
    print(x)
    pass