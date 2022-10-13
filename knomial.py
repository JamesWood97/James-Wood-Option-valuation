from finance import *


def k_nomial(T, sigma, r, q, S, E, mode, payoff, number_of_steps=1, k=2, american=False, lower_bound=None,upper_bound=None):
    s = sigma

    dt = T / number_of_steps
    binomial_number_of_steps = number_of_steps*(k-1)
    u,d,pu = get_binomial_values(T,binomial_number_of_steps,sigma,r,q,E,S,mode)
    pd = 1-pu
    u_values = [u ** i * d ** (k - 1 - i) for i in range(k)]
    p_values = [comb(k - 1, i) * pu ** i * pd ** (k - 1 - i) for i in range(k)]


    #create the underlying tree
    S_values = [[S]]
    for step_number in range(number_of_steps):
        previous_S_values = S_values[-1]
        new_S_values = [i*previous_S_values[0] for i in u_values]
        for i in range(1,len(previous_S_values)):
            new_S_values.append(previous_S_values[i] * u_values[-1])
        S_values.append(new_S_values)
    option_values = [payoff(x,E) for x in S_values[-1]]


    #backtrack
    for step_number in range(number_of_steps-1,-1,-1):
        previous_option_values = option_values
        option_values = []
        number_of_values_in_this_step = 1 + step_number * (k - 1)
        for value_index in range(number_of_values_in_this_step):
            val = 0
            underlying_S = S_values[step_number][value_index]
            for i in range(k):
                val += p_values[i]*previous_option_values[value_index+i]
            val *= exp(-1*r*dt)
            if upper_bound is not None:
                if underlying_S >= upper_bound:
                    option_values.append(0)
                    continue
            if lower_bound is not None:
                if underlying_S <= lower_bound:
                    option_values.append(0)
                    continue
            if american:
                option_values.append(max(payoff(underlying_S,E),val))
            else:
                option_values.append(val)
    return option_values[0]
