# Option valuation program
Program developed from my code that I wrote for my dissertation. It can value European, American and Barrier options. Running main allows data to be put in manually and method of valuation selected. Requires numpy

## Module infomation:
 
main.py contains the main function and functions for getting user input. It asks the user for various parameters for the option selected and the method for valuing the option

option.py contains a option class, that contains the attributes of an option (spot price, strike price, volatility of the underlying, any barriers etc)

tree.py contains a function for valuing a given option using a specified tree method. Takes an option object as an input 

fintiedifference.py contains a Finite difference object that can be passed option parameters to estimate the value of an option using various finite difference methods. Takes an option object as an input 

montecarlo.py contains methods for valuing options using the monte carlo method. Takes an option object as an input 

finance.py contains an assortment of mathematical functions used by the other modules, as well as functions for exact option valuation where applicable

matrix.py contains a Matrix class that supports arbitrarily sized matrices and matrix addition and multiplication as well as transposition, LU decomposition and other functions

unit_tests.py contains unit tests for tree, monte-carlo and fintie difference methods for European, American and Barrier options as well as tests for the option class itself.
