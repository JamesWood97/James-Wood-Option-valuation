import random
from math import exp
from finance import *
from matrix import *








def monte_carlo(option:Option, number_of_trials:int = 16):
    """
    Estimates the value of a european barrier-less option
    :param option: the option
    :param number_of_trials: number of randomly generated asset paths to take
    :return: a tuple, containing the estimated value and 95% confidence interval
    """

    estimated_values = []
    for i in range(number_of_trials):
        ep = random.normalvariate(0,1)
        Si = option.spot_price*exp((option.interest_rate-0.5*option.volatility**2)*option.time_until_expiry +
                                   ep*option.volatility*(option.time_until_expiry**0.5))
        Vi = option.payoff(Si)
        estimated_values.append(exp(-1*option.interest_rate*option.time_until_expiry)*Vi)
    am = sum(estimated_values)/number_of_trials
    b2m = (1/(number_of_trials-1)) * sum([(Vi - am)**2 for Vi in estimated_values])
    bm = b2m**0.5
    return am, (am - 1.96*bm*(number_of_trials**-0.5),am + 1.96*bm*(number_of_trials**-0.5))


def monte_carlo_barrier(option: Option, number_of_trials: int = 16, number_of_steps_per_path: int = 16):
    """
    Estimates the value of a european barrier option
    :param option: the option
    :param number_of_trials: number of randomly generated asset paths to take
    :param number_of_steps_per_path: the number of steps per path
    :return: a tuple, containing the estimated value and 95% confidence interval
    """
    estimated_values = []
    dt = option.time_until_expiry/number_of_steps_per_path
    lower_barrier = option.lower_barrier
    upper_barrier = option.upper_barrier
    for i in range(number_of_trials):
        path = [option.spot_price]
        valid_path = True
        for step in range(number_of_steps_per_path):
            ep = random.normalvariate(0,1)
            Si = path[-1]*exp((option.interest_rate-0.5*option.volatility**2)*dt + ep*option.volatility*(dt**0.5))
            if (lower_barrier is not None and Si < lower_barrier) or (upper_barrier is not None and Si > upper_barrier):
                valid_path = False
                break#this path is ignored as it passes though a barrier
            path.append(Si)
        if valid_path:
            Vi = option.payoff(path[-1])
            estimated_values.append(exp(-1*option.interest_rate*option.time_until_expiry)*Vi)
        else:
            estimated_values.append(0)
    am = sum(estimated_values)/number_of_trials
    b2m = (1/(number_of_trials-1)) * sum([(Vi - am)**2 for Vi in estimated_values])
    bm = b2m**0.5
    return am, (am - 1.96*bm*(number_of_trials**-0.5),am + 1.96*bm*(number_of_trials**-0.5))





"""
def arithmetic_avg(x):
    return sum(x)/len(x)

def geometric_avg(x):
    log_list = [log(i) for i in x]
    return exp(arithmetic_avg(log_list))


def monte_carlo_asian(T,sigma,r,S,E,payoff,averaging_function=geometric_avg,number_of_trials = 16,number_of_steps_per_path=16):
    estimated_values = []
    dt = T/number_of_steps_per_path
    for i in range(number_of_trials):
        path = [S]
        for step in range(number_of_steps_per_path):
            ep = random.normalvariate(0,1)
            Si = path[-1]*exp((r-0.5*sigma**2)*dt + ep*sigma*(dt**0.5))
            path.append(Si)
        avg = averaging_function(path)
        Vi = payoff(path[-1],avg,E)
        estimated_values.append(exp(-1*r*T)*Vi)
    am = sum(estimated_values)/number_of_trials
    b2m = (1/(number_of_trials-1)) * sum([(Vi - am)**2 for Vi in estimated_values])
    bm = b2m**0.5
    return am, (am - 1.96*bm*(number_of_trials**-0.5),am + 1.96*bm*(number_of_trials**-0.5))


def monte_carlo_american(T,sigma,r,q,S,E,payoff,number_of_paths = 16,number_of_steps_per_path=16):
    dt = T/number_of_steps_per_path
    estimated_values = []
    e = [exp(-1*r*dt*i) for i in range(number_of_steps_per_path+1)]


    for i in range(number_of_paths):
        path = [S]
        for step in range(number_of_steps_per_path):
            ep = random.normalvariate(0,1)
            dX = random.normalvariate(0,dt)
            Si = path[-1]*exp((r - 0.5 * sigma ** 2) * dt + ep * sigma * (dt ** 0.5))#path[-1]*(1 + (r*dt + sigma*dX))# #exp((r - 0.5 * sigma ** 2) * dt + ep * sigma * (dt ** 0.5))
            path.append(Si)

        option_values = [e[i]*payoff(path[i],E) for i in range(number_of_steps_per_path+1)]
        print(path,"\n",option_values,max(option_values))
        estimated_values.append(max(option_values))
    return sum(estimated_values)/len(estimated_values)




def plot():
    import matplotlib.pyplot as plt
    S = 10
    E = 9
    sigma = 0.1
    r = 0.06
    T = 1
    q = 0
    sol = call_exact_value(S, E, 0, T, sigma, r)
    values = []
    lower_c_i = []
    upper_c_i = []
    space = range(3, 15)
    for i in space:
        val, conv_int = monte_carlo(T, sigma, r, q, S, E, lambda x:max(x-E,0), number_of_trials=2 ** i)
        values.append(val)
        lower_c_i.append(conv_int[0])
        upper_c_i.append(conv_int[1])
    plt.fill_between(space, lower_c_i, upper_c_i, alpha=0.2, label="95% confidence interval", color='tab:orange')
    plt.plot(space, values, label="Estimated value", color='orange')
    plt.plot(space, [sol for x in space], linestyle='dashed', label="True solution")
    plt.xlabel('Amount of random paths taken')
    plt.ylabel('Estimated Value')
    plt.legend(loc='upper right')
    labels = [2 ** i for i in space]
    plt.xticks(space, labels)
    plt.show()


def multivariable_monte_carlo(S_values,sigmas,rho_matrix: Matrix,r,T,payoff,number_of_trials = 16):
    estimated_option_values = []
    M = rho_matrix.get_chomsky_decomp()
    for i in range(number_of_trials):
        ep_values = []
        end_S_values = []
        for i in range(len(S_values)):

            ep = random.normalvariate(0, 1)
            ep_values.append(ep)

        corrilated_ep_values = []
        ep_vector = Matrix(ep_values)
        ep_vector.transpose()

        corrilated_ep_values_vector = M*ep_vector
        for i in range(len(S_values)):
            S_val = S_values[i]*exp((r-0.5*sigmas[i]**2)*T + corrilated_ep_values_vector[i]*sigmas[i]*(T**0.5))
            end_S_values.append(S_val)

        estimated_option_values.append(payoff(end_S_values))

    return exp(-1*r * T) * sum(estimated_option_values)/len(estimated_option_values)
"""


