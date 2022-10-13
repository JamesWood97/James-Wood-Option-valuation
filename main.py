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
    avalible_methods_for_option_type = {"european":["Binomial", "Trinomial", "Finite difference", "Monte-Carlo"],
                                        "american":["binomial", "finite difference"]}

    r = get_value("Interest rate: ")
    sigma = get_value("Volatility: ")
    E = get_value("Strike Price: ")
    S = get_value("Spot Price: ")

    option_type_index = get_choice("Option type:",["European", "American"])
    option_type = {0: "european", 1: "american"}[option_type_index]
    method_to_use = get_choice("Method to use:", avalible_methods_for_option_type[option_type])

if __name__ == "__main__":
    main()