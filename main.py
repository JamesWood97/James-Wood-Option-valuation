from knomial import *
from finitedifference import *

def get_value(question:str, conversion_function = lambda x:float(x)):
    while True:
        value = input(question)
        try:
            return conversion_function(value)
        except ValueError:
            print("Invalid number")

def get_choice(question:str, choice_strings:list[str]):
    print(question)
    for i, choice_string in enumerate(choice_strings):
        print(choice_string + " ["+str(i+1)+"]")
    while True:
        choice_number = get_value("", lambda x: int(x))
        if 1 <= choice_number <= len(choice_strings):
            return choice_number-1





def main():
    avalible_methods_for_option_type = {"european": ["binomial", "trinomial", "finite difference", "monte carlo"],
                                        "american": ["binomial", "finite difference"]}

    option_type_index = get_choice("Option type:",["European", "American"])
    is_american = bool(option_type_index)
    method_to_use = get_choice("Method to use:", avalible_methods_for_option_type[{True: "american", False: "european"}])

    r = get_value("Interest rate: ")
    sigma = get_value("Volatility: ")
    S = get_value("Spot Price: ")
    T = get_value("Years until expiry: ")
    q = get_value("Dividend rate")

    if method_to_use == "binomial":
        E = get_value("Strike Price: ")
        number_of_steps = get_value("Number of Steps: ", conversion_function=lambda x: float(x))
        estimated_value = k_nomial(T, sigma, r, q, S, E, lambda x:max(x-E,0), number_of_steps=number_of_steps, k=2,
                                   american=is_american, lower_bound=None, upper_bound=None)



    print(estimated_value)





if __name__ == "__main__":
    main()
