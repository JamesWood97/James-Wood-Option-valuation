from knomial import *
from finitedifference import *
from montecarlo import *

def get_value(question:str, conversion_function = lambda x:float(x)):
    """
    Gets the user input and returns it in the type specified in the conversion_function. If an invalid input is given
    it gets the user input again until a valid input is given
    :param question: the question the user is asked
    :param conversion_function: function that converts the input from a string to the desired type. defaults to float
    :return: returns the value inputted in as the type specified in the conversion_function
    """
    while True:
        value = input(question)
        try:
            return conversion_function(value)
        except ValueError:
            print("Invalid number")

def get_choice(question:str, choice_strings:list[str], return_string = False):
    """

    :param question: the question the user is asked
    :param choice_strings: list containing a string saying each choice, presented to the user
    :param return_string: if the string selected should be returned in place of the index selected
    :return: if return string is False it returns the index of the choice, else it returns the string shown to the user as the choice
    """
    print(question)
    for i, choice_string in enumerate(choice_strings):
        print(choice_string + " ["+str(i+1)+"]")
    while True:
        choice_number = get_value("", lambda x: int(x))
        if 1 <= choice_number <= len(choice_strings):

            if return_string:
                return choice_strings[choice_number - 1]

            return choice_number-1



def get_barriers(S):
    """
    gets barriers for the option from the user
    :param S: the starting value of the asset
    :return: returns a lower barrier value and upper barrier value. If a barrier has no value (e.g doesnt exist) it is set to None
    """
    number_of_barriers = int(get_choice("How many barriers?", ["0", "1", "2"], return_string=True))

    if number_of_barriers == 0:
        return None, None

    lower_barrier = None
    upper_barrier = None

    for barrier in range(number_of_barriers):
        valid_barrier_chosen = False
        while not valid_barrier_chosen:
            barrier_value = get_value("Barrier value")
            if barrier_value < S:
                if lower_barrier is None:
                    lower_barrier = barrier_value
                    valid_barrier_chosen = True
                else:
                    print("A lower barrier has already been chosen")
            if barrier_value > S:
                if upper_barrier is None:
                    upper_barrier = barrier_value
                    valid_barrier_chosen = True
                else:
                    print("A upper barrier has already been chosen")

    return lower_barrier, upper_barrier




def main():
    avalible_methods_for_option_type = {"european": ["binomial", "trinomial", "finite difference", "monte carlo",
                                                     "large branched tree"],
                                        "american": ["binomial", "finite difference"]}

    option_type_index = get_choice("Option type:",["European", "American"])
    is_american = bool(option_type_index)
    method_to_use = get_choice("Method to use:",
                               avalible_methods_for_option_type[{True: "american", False: "european"}[is_american]],
                               return_string=True)

    r = get_value("Interest rate: ")
    sigma = get_value("Volatility: ")
    S = get_value("Spot Price: ")
    T = get_value("Years until expiry: ")
    E = get_value("Strike Price: ")
    #q = get_value("Dividend rate")
    q = 0
    lower_barrier, upper_barrier = get_barriers(S)

    option_type_index = get_choice("Call or put?", ["Call","Put"], return_string=False)
    if option_type_index == 0:
        payoff = lambda x:max(x-E,0)
    else:
        payoff = lambda x: max(E-x, 0)

    if method_to_use == "binomial":
        number_of_steps = get_value("Number of Steps: ", conversion_function=lambda x: int(x))
        mode = get_choice("Binomial method to use:", ["Cox-Ross-Rubinstein", "Jarrow-Rudd", "Leisen-Reimer"],
                          return_string=True)
        estimated_value = k_nomial(T, sigma, r, q, S, E, mode, payoff, number_of_steps=number_of_steps,
                                   k=2, american=is_american, lower_bound=lower_barrier, upper_bound=upper_barrier)

    elif method_to_use == "trinomial":
        number_of_steps = get_value("Number of Steps: ", conversion_function=lambda x: int(x))
        mode = get_choice("Binomial method to use:", ["Cox-Ross-Rubinstein", "Jarrow-Rudd", "Leisen-Reimer"],
                          return_string=True)
        estimated_value = k_nomial(T, sigma, r, q, S, E, mode, payoff, number_of_steps=number_of_steps,
                                   k=3, american=is_american, lower_bound=lower_barrier, upper_bound=upper_barrier)

    elif method_to_use == "large branched tree":
        number_of_steps = get_value("Number of Steps: ", conversion_function=lambda x: int(x))
        number_of_branches_per_node = get_value("Number of Steps: ", conversion_function=lambda x: int(x))
        mode = get_choice("Underlying ninomial method to use:", ["Cox-Ross-Rubinstein", "Jarrow-Rudd", "Leisen-Reimer"],
                          return_string=True)
        estimated_value = k_nomial(T, sigma, r, q, S, E, mode, payoff, number_of_steps=number_of_steps,
                                   k=number_of_branches_per_node, american=is_american, lower_bound=lower_barrier,
                                   upper_bound=upper_barrier)

    elif method_to_use == "finite difference":
        number_of_steps = get_value("Number of Steps: ", conversion_function=lambda x: int(x))
        mode = get_choice("Fintie difference method to use:", ["Explicit", "Implicit", "Crank-Nicolson"],
                          return_string=True)
        fdm_obj = FDM(T, sigma, r, q, S, E, payoff, number_of_steps, number_of_t_nodes=None, dx=None, mode =mode,
                      lower_barrier=lower_barrier, upper_barrier=upper_barrier, american=is_american)
        estimated_value = fdm_obj.get_value_estimation_at_start(S)
    
    elif method_to_use == "monte carlo":
        if lower_barrier is None and upper_barrier is None:
            number_of_trials = get_value("Number of paths: ", conversion_function=lambda x: int(x))
            estimated_value, conf_interval_095 = monte_carlo(T, sigma, r, q, S, E, payoff,
                                                             number_of_trials=number_of_trials)
        else:
            number_of_trials = get_value("Number of paths: ", conversion_function=lambda x: int(x))
            number_of_steps_per_path = get_value("Number of steps per path: ", conversion_function=lambda x: int(x))
            estimated_value, conf_interval_095 = monte_carlo_barrier(T, sigma, r, S, E,
                                                                     payoff, lower_barrier=lower_barrier,
                                                                     upper_barrier=upper_barrier,
                                                                     number_of_trials=number_of_trials,
                                                                     number_of_steps_per_path=number_of_steps_per_path)

    else:
        raise Exception(method_to_use,"is not a valid method")

    print("Estimated option value:",estimated_value)





if __name__ == "__main__":
    main()
