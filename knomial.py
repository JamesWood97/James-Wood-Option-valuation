from finance import *


def tree(option: Option, mode: str, number_of_steps: int = 1, number_of_branches_per_node: int = 2):
    """
    Main tree method. Takes na option class, the underlying mode (Cox-Ross-Rubinstien, Jarrow-Rudd or Leisen Reimer) and
     the number fo steps and branches per step
    :param option: The option to be valued
    :param mode: the underlying mode (Cox-Ross-Rubinstien, Jarrow-Rudd or Leisen Reimer)
    :param number_of_steps: the number of steps to take
    :param number_of_branches_per_node: the number of branches from each node in the tree
    :return: returns an estimated value of the option
    """
    S, E, r, sigma, q, T = option.return_parameters()
    dt = T / number_of_steps
    binomial_number_of_steps = number_of_steps * (number_of_branches_per_node - 1)
    u, d, pu = get_binomial_values(T, binomial_number_of_steps, sigma, r, q, E, S, mode)
    pd = 1 - pu

    # the amount the asset changes in value for each branch
    u_values = [u ** i * d ** (number_of_branches_per_node - 1 - i) for i in range(number_of_branches_per_node)]

    # the probability of each branch
    p_values = [comb(number_of_branches_per_node - 1, i) * pu ** i * pd ** (number_of_branches_per_node - 1 - i) for i
                in range(number_of_branches_per_node)]

    # create the underlying tree
    S_values = [[option.spot_price]]
    for step_number in range(number_of_steps):
        previous_S_values = S_values[-1]
        new_S_values = [i * previous_S_values[0] for i in u_values]
        for i in range(1, len(previous_S_values)):
            new_S_values.append(previous_S_values[i] * u_values[-1])
        S_values.append(new_S_values)
    option_values = [option.payoff(x) for x in S_values[-1]]

    # backtrack
    for step_number in range(number_of_steps - 1, -1, -1):
        previous_option_values = option_values
        option_values = []
        number_of_values_in_this_step = 1 + step_number * (number_of_branches_per_node - 1)
        for value_index in range(number_of_values_in_this_step):
            val = 0
            underlying_S = S_values[step_number][value_index]
            for i in range(number_of_branches_per_node):
                val += p_values[i] * previous_option_values[value_index + i]
            val *= exp(-1 * r * dt)

            if option.upper_barrier is not None:
                if underlying_S >= option.upper_barrier:
                    option_values.append(0)
                    continue
            if option.lower_barrier is not None:
                if underlying_S <= option.lower_barrier:
                    option_values.append(0)
                    continue

            if option.is_american:
                option_values.append(max(option.payoff(underlying_S), val))
            else:
                option_values.append(val)
    return option_values[0]
