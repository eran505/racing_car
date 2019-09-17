
from random import choices
class action_drive:

    def __init__(self,speed,state):
        self.speed_to_add=speed
        self.cur_state = state
        self.step_cost=-0.05
        self.cost=0.5
        self.absolute_max_speed=2
        self.action_list = [(0,0),(0,1),(0,-1),(1,1),(1,0),(1,-1),(-1,-1),(-1,1),(-1,0)]

    def set_state(self,state):
        self.cur_state=state

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
            print (a[0])
            self.speed_to_add=a[0]

    def apply_action(self,agent_id):
        new_speed = self.change_speed(agent_id)
        pos_cur = self.cur_state.get_agent_position(agent_id)
        new_pos = [pos_cur[i] + new_speed[i] for i in range(len(new_speed))]
        self.cur_state.set_agent_position(agent_id,new_pos)
        budget_cur = self.cur_state.get_agent_budget(agent_id)
        self.cur_state.set_agent_budget(agent_id,budget_cur - self.cost)

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

    def get_expected_reward(self,player_id):
        s_state = self.cur_state.get_deep_copy_state()
        action_list = [(0,0),(0,1),(0,-1),(1,1),(1,0),(1,-1),(-1,-1),(-1,1),(-1,0)]
        d_action={}
        d_wall={}
        state_reward={}
        for action_a in action_list:
            self.speed_to_add=action_a
            self.cur_state = s_state.get_deep_copy_state()
            self.apply_action(player_id)
            #r = self.cur_state.get_reward_by_id(player_id)
            r=self.step_cost
            bol_wall = self.cur_state.is_wall_all()

            str_state=self.cur_state.state_to_string_no_budget()
            d_action[action_a]=str_state
            state_reward[str_state]=r
            d_wall[str_state] = bol_wall

        return state_reward,d_action,d_wall

    @staticmethod
    def keywithmaxval(d):
        """ a) create a list of the dict's keys and values;
            b) return the key with the max value"""
        v = list(d.values())
        k = list(d.keys())
        return k[v.index(max(v))]

if __name__ == "__main__":
    pass