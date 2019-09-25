
from itertools import product


def reward_func(agent_in,info,string,reward,gurd_symbol='B'):
    if string == 'goal':
        for agent_i in agent_in[gurd_symbol]:
            agent_i.update_reward(reward)

    if string == 'collusion':
        for collusion_i in info:
            for item in collusion_i:
                if item['team'] == gurd_symbol:
                    for agent_i in agent_in[gurd_symbol]:
                        if agent_i.get_id() == item['p']:
                            agent_i.update_reward(reward)

    if string == 'wall':
        agent_in.update_reward(reward)



def init_dict_state_helper(x,y,max_speed=2):
    ctr=0
    list_player=[]
    for x_i in range(x):
        for y_i in range(y):
            for s_x in range(-max_speed,max_speed+1):
                for s_y in range(-max_speed,max_speed+1):
                    for b in range(10,11):
                        str_state =  ("{}_{}_{}".format((x_i,y_i),(s_x,s_y),b))
                        list_player.append(str_state)
                        ctr+=1
    print("ctr= ",ctr)
    return list_player



def construct_map_state(x,y,max_speed,num_playerz,order_list_player_name):
    ctr=0
    map_state={}
    list_of_state = init_dict_state_helper(x,y,max_speed)
    states_list = list(product(list_of_state, repeat=num_playerz))
    for state in states_list:
        state_i = [None] * num_playerz
        for p in range(len(order_list_player_name)):
            state_i[p] = "{}_{}".format(order_list_player_name[p], state[p])
        state_str = '|'.join(state_i)
        map_state[state_str] = ctr
        ctr += 1
    return map_state

if __name__ == "__main__":
    pass