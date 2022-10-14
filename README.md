# Option valuation program
Program developed from my code I wrote for my dissertation. It can value European, American and Barrier options. Running main allows data to be put in manually and method of valuation selected. Requires numpy

Module infomation:
 
main.py contains the main function and functions for getting user input. It asks the user for various parameters for the option selected amd the method for valuing the option

knomial.py contains a function for valuing a given option using a specified tree method. 

fintiedifference.py contains a Fintie difference object thta can eb passed option parameters to estimate the value of an option using finite difference methods

monte carlo.py contains methods for valuing options using the monte carlo method

finace.py contains an assortment of mathematical functions used by the other modules, as well as functions for exact option valuation where applicable

matrix.py contains a Matrix class that supports arbitrarily sized matrices and matrix addition and multiplication as well as transposition, LU decomposition and other functions