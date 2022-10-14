from math import *
from option import *

def inv_erf(x):
    y = 0
    c = [1]
    for k in range(20):
        y += c[k]/(2*k+1) * ( ((pi**0.5)/2 * x) ** (2*k+1) )
        c.append(sum([c[m]*c[k-1-m]/((m+1)*(2*m+1)) for m in range(k)]))
    return y

def sgn(x):
    if x == 0:
        return 0
    return abs(x)/x

def mean(array):
    return sum(array)/len(array)

def geometric_avg(array):
    avg = 1
    for element in array:
        avg *= element
    return avg ** (1/len(array))


def peizer_pratt_inversion(x,n):
    return 0.5 + sgn(x)*0.5*(1- exp(-1* (x/(n+(1/3)))**2 * (n+1/6)) )**0.5

def get_leisen_reimer_values(T,sigma,r,q,E,S,number_of_steps):
    dt = T/number_of_steps
    d1 = 1/(sigma*(T-0)**0.5)*(log(S/E) + ((r-q) + (sigma*sigma/2)) * (T-0))
    d2 = d1 - sigma*((T-0)**0.5)
    p2 = peizer_pratt_inversion(d2,number_of_steps)
    p1 = peizer_pratt_inversion(d1,number_of_steps)
    u = exp((r-q)*dt)*p1/p2
    d = exp((r-q)*dt)*(1-p1)/(1-p2)
    return u,d,p2

def intergrate(f,a,b,h_amount = 1000000,type="midpoint"):
    h = (b-a)/h_amount
    area = 0
    intergration_func = {"midpoint":midpoint,"trapezoidal":trapezoidal,"simpsons":simpsons}[type]
    for i in range(h_amount):
        subinterval_a = a+h*i
        subinterval_b = a+h*(i+1)
        area += intergration_func(f,subinterval_a,subinterval_b)
    return area


def midpoint(f,a,b):
    return (b-a)*f((a+b)/2)

def trapezoidal(f,a,b):
    return (b-a)*(f(a) + f(b))/2

def simpsons(f,a,b):
    return (b-a)*(f(a) + 4*f((a+b)/2) + f(b))/6

def normal_cumulative_distribution(x,integration_type="simpsons",h_amount = 1000000):
    return 1/((2*pi)**0.5) * intergrate(lambda z:exp(-1*z*z/2),-110,x,h_amount=h_amount,type=integration_type)

def normal_probability_density(x):
    return 1/((2*pi)**0.5) * exp(-1*x*x/2)


def exchange_option_exact_value(S1,S2,sigma1,sigma2,rho,D1,D2,q1,q2,T):
    nu = S1/S2
    E = q1/q2
    sigmahat = (sigma1**2 - 2*rho*sigma1*sigma2 + sigma2**2)**0.5
    val = call_exact_value(nu,E,0,T,sigmahat,D2,dividend_rate=D1)
    return q1*S2*val


def call_exact_value(S,E,t,T,sigma,r,dividend_rate = 0,integration_type="simpsons",number_of_integral_steps=100000):
    d1 = 1/(sigma*(T-t)**0.5)*(log(S/E) + (r + (sigma*sigma/2)) * (T-t))
    d2 = d1 - sigma*((T-t)**0.5)
    return normal_cumulative_distribution(d1,integration_type=integration_type,h_amount=number_of_integral_steps)*S*exp(-1*dividend_rate*(T-t)) - normal_cumulative_distribution(d2,integration_type=integration_type,h_amount=number_of_integral_steps)*E*exp(-1*r*(T-t))


def down_and_out_call_exact_value(S,E,t,T,sigma,r,B,dividend_rate = 0,integration_type="simpsons",number_of_integral_steps=100000):
    if B > S:
        return 0
    k = r/(0.5*sigma**2)
    return call_exact_value(S,E,t,T,sigma,r,dividend_rate = dividend_rate,integration_type=integration_type,number_of_integral_steps=number_of_integral_steps) - (S/B)**(1-k) * call_exact_value(B**2 / S,E,t,T,sigma,r,dividend_rate = dividend_rate,integration_type=integration_type,number_of_integral_steps=number_of_integral_steps)

def down_and_in_call_exact_value(S,E,t,T,sigma,r,B,dividend_rate = 0,integration_type="simpsons",number_of_integral_steps=100000):
    k = r/(0.5*sigma**2)
    return (S/B)**(1-k) * call_exact_value(B**2 / S,E,t,T,sigma,r,dividend_rate = dividend_rate,integration_type=integration_type,number_of_integral_steps=number_of_integral_steps)

def put_exact_value(S,E,t,T,sigma,r,dividend_rate = 0,integration_type="simpsons",number_of_integral_steps=100000):
    d1 = 1/(sigma*(T-t)**0.5)*(log(S/E) + (r + (sigma*sigma/2)) * (T-t))
    d2 = d1 - sigma*((T-t)**0.5)
    return normal_cumulative_distribution(-1*d2,integration_type=integration_type,h_amount=number_of_integral_steps)*E*exp(-1*r*(T-t)) - normal_cumulative_distribution(-1*d1,integration_type=integration_type,h_amount=number_of_integral_steps)*S*exp(-1*dividend_rate*(T-t))

def get_binomial_values(T,number_of_steps,sigma,r,q,E,S,mode):
    mode = mode.lower().replace("-", "").replace(" ", "")
    if mode in ["coxrossrubinstein","crr"]:
        dt = T/number_of_steps
        pu = 0.5
        d = exp((r-q) * dt) * (1 - (exp(sigma * sigma * dt) - 1) ** 0.5)
        u = exp((r-q) * dt) * (1 + (exp(sigma * sigma * dt) - 1) ** 0.5)
    elif mode in ["jarrowrudd","jr"]:
        dt = T / number_of_steps
        A = 0.5*(exp(-1*(r-q)*dt)+exp(((r-q)+sigma**2)*dt))
        u = A + (A**2 - 1)**0.5
        d = 1/u
        pu = exp((r-q)*dt) - d
        pu /= u - d
    elif mode in ["leisenreimer","lr"]:
        u,d,pu = get_leisen_reimer_values(T, sigma, r, q, E, S, number_of_steps)
    else:
        raise Exception(mode+" not valid!")
    return u,d,pu


def f(u,mean,variance):
    M = mean
    V = variance
    return ( (V + M**2 - M)*u - (M-1) ) / ((u-1)*(u*u-1))

def g(u,mean,variance):
    M = mean
    V = variance
    return ( (V + M**2 - M)*u*u - (M-1)*u*u*u ) / ((u-1)*(u*u-1))