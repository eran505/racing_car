



def reward_func(agent_in,info,string,gurd_symbol='B'):
    if string == 'goal':
        for agent_i in agent_in[gurd_symbol]:
            agent_i.update_reward(-10)

    if string == 'collusion':
        for collusion_i in info:
            for item in collusion_i:
                if item['team'] == gurd_symbol:
                    for agent_i in agent_in[gurd_symbol]:
                        if agent_i.get_id() == item['p']:
                            agent_i.update_reward(10)

    if string == 'wall':
        agent_in.update_reward(-1)



if __name__ == "__main__":
    pass