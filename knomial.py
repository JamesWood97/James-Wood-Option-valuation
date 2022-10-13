from math import *
from finance import *
import time




#main method for trees. type can be "european" or "american". k is the number of branches per node






def k_nomial(T, sigma, r, q, S, E, mode, payoff, number_of_steps=1, k=2, type="european",lower_bound=None,upper_bound=None):
    #print("-" * 10)
    #print(str(k) + "-nomial method")
    #print("number of steps:", number_of_steps)
    s = sigma

    dt = T / number_of_steps
    binomial_number_of_steps = number_of_steps*(k-1)
    u,d,pu = get_binomial_values(T,binomial_number_of_steps,sigma,r,q,E,S,mode)
    pd = 1-pu

    #print([d,u])
    #print([pd,pu])
    u_values = [u ** i * d ** (k - 1 - i) for i in range(k)]
    p_values = [comb(k - 1, i) * pu ** i * pd ** (k - 1 - i) for i in range(k)]
    #print("u_values",u_values)
    #print("p_values",p_values)
    #print(" ")
    S_values = [[S]]
    for step_number in range(number_of_steps):
        previous_S_values = S_values[-1]
        new_S_values = [i*previous_S_values[0] for i in u_values]
        for i in range(1,len(previous_S_values)):
            new_S_values.append(previous_S_values[i] * u_values[-1])
        S_values.append(new_S_values)
    S_tree_constructed_time = time.perf_counter_ns()
    #print("\ngetitng option values")
    option_values = [payoff(x,E) for x in S_values[-1]]

    #       print(S_values)

    for step_number in range(number_of_steps-1,-1,-1):
        #print("-"*10)
        #print(option_values)
        previous_option_values = option_values
        option_values = []
        number_of_values_in_this_step = 1 + step_number * (k - 1)
        for value_index in range(number_of_values_in_this_step):
            val = 0
            underlying_S = S_values[step_number][value_index]
            for i in range(k):
                val += p_values[i]*previous_option_values[value_index+i]
            val *= exp(-1*r*dt)
            #print(step_number, value_index, val, S_values[step_number][value_index])
            if upper_bound is not None:
                if underlying_S >= upper_bound:
                    option_values.append(0)
                    continue
            if lower_bound is not None:
                if underlying_S <= lower_bound:
                    option_values.append(0)
                    continue
            if type == "american":
                option_values.append(max(payoff(underlying_S,E),val))
            else:
                option_values.append(val)
        #print(option_values)
        """
    end_time = time.perf_counter_ns()
    print("value", option_values[0])
    print("Type:",type)
    print("S tree construction time", S_tree_constructed_time - start_time)
    print("backtracking time", end_time - S_tree_constructed_time)  # 40281841800  34923876300 224940355500
    print("total time", end_time - start_time)"""
    return option_values[0]





"""def k_nomial(T, sigma, r, q, S, E, mode, payoff, number_of_steps=1, k=2, american=False):
    print("-" * 10)
    print(str(k) + "-nomial method")
    print("number of steps:", number_of_steps)
    s = sigma

    n_nomial_dt = T / number_of_steps
    binomial_number_of_steps = number_of_steps*(k-1)
    u,d,pu = get_binomial_values(T,binomial_number_of_steps,sigma,r,q,E,S,mode)
    pd = 1-pu

    print([d,u])
    print([pd,pu])
    u_values = [u ** i * d ** (k - 1 - i) for i in range(k)]
    p_values = [comb(k - 1, i) * pu ** i * pd ** (k - 1 - i) for i in range(k)]
    print("u_values",u_values)
    print("p_values",p_values)
    print(" ")
    start_time = time.perf_counter_ns()
    S_values = [S]
    for step_number in range(number_of_steps):
        previous_S_values = S_values
        S_values = [i*previous_S_values[0] for i in u_values]
        for i in range(1,len(previous_S_values)):
            S_values.append(previous_S_values[i] * u_values[-1])
    S_tree_constructed_time = time.perf_counter_ns()
    #print("\ngetitng option values")
    option_values = [payoff(x,E) for x in S_values]
    #print(option_values)

    for step_number in range(number_of_steps,0,-1):
        previous_option_values = option_values
        option_values = []
        step_number -= 1
        number_of_values_in_this_step = 1 + step_number * (k - 1)
        for value_index in range(number_of_values_in_this_step):
            val = 0
            for i in range(k):
                val += p_values[i]*previous_option_values[value_index+i]
            val *= exp(-1*r*n_nomial_dt)
            option_values.append(val)
        #print(option_values)
    end_time = time.perf_counter_ns()
    print("value", option_values[0])
    print("S tree construction time", S_tree_constructed_time - start_time)
    print("backtracking time", end_time - S_tree_constructed_time)  # 40281841800  34923876300 224940355500
    print("total time", end_time - start_time)
    return option_values[0], end_time - start_time"""