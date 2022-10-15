class Option:
    def __init__(self, spot_price: float | int, strike_price: float | int, time_until_expiry: float | int,
                 volatility: float | int,
                 interest_rate: float | int, lower_barrier: float | int = None,
                 upper_barrier: float | int = None, is_american: bool = False, payoff_function=None,
                 dividend_rate: float = 0):
        """
        Constructor for option class
        :param spot_price: The spot price of the option. Can be int or float
        :param strike_price: The strike price of the option. Can be int or float
        :param time_until_expiry: Time until the option expires. if volitility and interest rate are given as yearly values, this will be yearly too
        :param volatility: The volatility of the underlying asset
        :param interest_rate: The interest rate
        :param lower_barrier: The lower barrier. If there is no lower barrier, this should be None
        :param upper_barrier: The upper barrier. If there is no upper barrier, this should be None
        :param is_american: If the option is american (as opposed to european)
        :param payoff_function: The payoff function. For example, for a call with asset price S with strike price E this would be lambda S,E:max(S-E,0)
        """
        self.spot_price = spot_price
        self.strike_price = strike_price
        self.time_until_expiry = time_until_expiry
        self.volatility = volatility
        self.interest_rate = interest_rate
        self.lower_barrier = lower_barrier
        self.upper_barrier = upper_barrier
        self.is_american = is_american
        self.payoff = lambda x: payoff_function(x,self.strike_price)# when called, this DOES NOT take the strike price as a parameter
        self.dividend_rate = dividend_rate

    def return_parameters(self):
        return self.spot_price, self.strike_price, self.interest_rate, self.volatility, self.dividend_rate,\
               self.time_until_expiry
        #S, E, r, sigma, q, T
