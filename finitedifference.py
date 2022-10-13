import numpy as np
from matrix import *

def sum_mine(array):
    total = 0
    for item in array:
        total += item
    return total







#this class has several attrributes
#T, sigma, r, q, S, E, payoff, number_of_x_nodes, number_of_t_nodes=None should be self explanatory
#mode is what type, so explicit, implicit or crank-nicolson (cn works too)
#lower_barrier=None, upper_barrier=None, are locations of barriers. option is assuemd to be up/down and out if a barrier is placed
#centre where the centr eof the mesh should be. can be "S" or "E"
# american if the optiomn should be american



#
#To use this, create a fdm object like so
#fdmobject = FDM(T, sigma, r, q, S, E, payoff, number_of_x_nodes)
#then to get the value of the option at price S call this
#estimated value = fdmobject.get_value_estimation_at_start(S)





class FDM:
    def __init__(self, T, sigma, r, q, S, E, payoff, number_of_x_nodes, number_of_t_nodes=None, dx=None, mode ="cn", lower_barrier=None, upper_barrier=None, centre="S", inversion_type="numpy", american=False):
        if dx is None:
            dx = 8 / number_of_x_nodes
        if number_of_t_nodes is None:
            number_of_t_nodes = max(int(number_of_x_nodes / 8), 2)
        if lower_barrier is None and upper_barrier is None:
            if centre == "S":
                x_bounds = [np.log(S/E) - ((number_of_x_nodes - 1) / 2) * dx, np.log(S / E) + ((number_of_x_nodes - 1) / 2) * dx]
            else:
                x_bounds = [-1.5,1.5]
                x_bounds.sort()
                dx = (x_bounds[1] - x_bounds[0]) / (number_of_x_nodes - 1)
        elif upper_barrier is None:
            x_bounds = [np.log(lower_barrier / E),
                        np.log(lower_barrier / E) + (number_of_x_nodes - 1) * dx]
        elif lower_barrier is None:
            x_bounds = [np.log(upper_barrier / E) - (number_of_x_nodes - 1) * dx,
                        np.log(upper_barrier / E)]
        else:
            x_bounds = [np.log(lower_barrier / E),
                        np.log(upper_barrier / E)]
            dx = (x_bounds[1] - x_bounds[0]) / (number_of_x_nodes - 1)
        #print("x_bounds:",x_bounds)

        #print(dx, x_bounds)
        t_bounds = [T,0]
        tau_bounds = [0.5*(T-t)*sigma**2 for t in t_bounds]
        dtau = (tau_bounds[1] - tau_bounds[0])/(number_of_t_nodes - 1)
        self.dx = dx
        self.dtau = dtau
        self.get_FDM_values(S, E, T, sigma, r)
        self.number_of_t_values = number_of_t_nodes
        self.number_of_x_nodes = number_of_x_nodes
        self.american = american
        #print("alpha:",self.alpha)


        k = self.k
        self.payoff = payoff
        v_payoff = lambda x: payoff(E*np.exp(x), E)/E
        u_payoff = lambda x:np.exp(0.5*(k-1)*x)*v_payoff(x)
        self.u_payoff = u_payoff

        #print(np.log(S/E), dx, int((number_of_x_values - 1)/2), int((number_of_x_values - 1)/2)*dx )

        #print("dx",dx,"dt",dtau)
        if lower_barrier is None:
            t_lower_boundary = lambda t: u_payoff(-1*2**5)#0
        else:
            t_lower_boundary = lambda t: 0

        if upper_barrier is None:
            t_upper_boundary = lambda t: u_payoff(-1*2**5)#0
        else:
            t_upper_boundary = lambda t: 0

        x_boundary = u_payoff

        self.solve(x_bounds, tau_bounds, number_of_x_nodes, number_of_t_nodes, x_boundary, t_lower_boundary,
                   t_upper_boundary, mode=mode, lower_barrier=lower_barrier, upper_barrier=upper_barrier,
                   inversion_type=inversion_type)

        #print(self,"\n")
        self.get_BSE_values()

    def solve(self,x_bounds,tau_bounds,number_of_x_values,number_of_t_values,x_boundary,t_lower_boundary,t_upper_boundary,mode = "implicit",lower_barrier=None, upper_barrier=None,sol=None, inversion_type="numpy"):
        self.number_of_x_nodes = number_of_x_values
        self.number_of_t_values = number_of_t_values
        mode = mode.lower()
        mode = mode.replace("_","").replace(" ","").replace("-","")
        dtau = self.dtau
        dx = self.dx
        self.x_bounds = x_bounds
        self.tau_bounds = tau_bounds
        self.x_values = [self.x_bounds[0] + x_index * dx for x_index in range(number_of_x_values)]







        self.tau_values = [self.tau_bounds[0] + t_index * dtau for t_index in range(number_of_t_values)]
        self.heat_values = [[None for i in range(number_of_t_values)] for j in range(number_of_x_values)]
        self.true_values = [[None for i in range(number_of_t_values)] for j in range(number_of_x_values)]



        for x_index in range(number_of_x_values):
            x = self.x_bounds[0] + x_index*dx
            #print("x",x,x_boundary(x))
            self[x_index,0] = x_boundary(x)
        for t_index in range(number_of_t_values):
            tau = self.tau_bounds[0] + t_index * dtau
            self[0, t_index] = t_lower_boundary(tau)
            self[-1, t_index] = t_upper_boundary(tau)
        alpha = dtau/(dx**2)
        self.alpha = alpha
        #print("alpha",alpha)
       # print("r",r)
        if mode == "explicit":
            for t_index in range(0, number_of_t_values - 1):
                for x_index in range(1,number_of_x_values-1):
                    #print(self)
                    self[x_index,t_index+1] = (1-2*alpha)*self[x_index,t_index] + alpha*(self[x_index+1,t_index] + self[x_index-1,t_index])
                    if self.american:
                        x = self.x_values[x_index]
                        E = self.E
                        tau = self.tau_values[t_index+1]
                        if E*self[x_index,t_index+1]/exp((self.k - 1)*x/2 + (self.k + 1)**2 * tau/4) < self.payoff(E*exp(x),E):
                            self[x_index,t_index+1] = self.payoff(E*np.exp(x), E)/E * exp((self.k-1)*x/2 +  (self.k + 1)**2 * tau/4)
        elif mode == "full_explicit":
            self.solve_full_explicit()#does nothing/depreacted
        elif mode == "implicit":
            self.implicit(inversion_type)
        elif mode == "cn" or mode == "cranknicolson":
            self.crank_nicolson(inversion_type)

        self.errors = [[None for i in range(number_of_t_values)] for j in range(number_of_x_values)]
        if sol is not None:
            for x_index in range(0, self.number_of_x_nodes):
                for t_index in range(0, self.number_of_t_values):
                    val = self[x_index,t_index]
                    x = self.x_values[x_index]
                    t = self.tau_bounds[t_index]
                    solution = sol(x,t)
                    if solution != 0 and val != 0:
                        error = abs((val - solution)/solution)
                        if x_index == 99:
                            print(t_index,val,solution,error)
                    elif solution != 0:
                        error = abs(solution)
                    else:
                        error = abs(val - solution)
                    self.errors[x_index][t_index] = error


    def __repr__(self):
        string = ""
        for i in range(self.number_of_x_nodes):
            for j in range(self.number_of_t_values):
                label = str(self.heat_values[i][j])
                string += label + (25 - len(label))*" "
            string += "\n"
        return string

    def get_error_string(self):
        string = ""
        for i in range(self.number_of_x_nodes):
            for j in range(self.number_of_t_values):
                label = str(self.errors[i][j])
                string += label + (25 - len(label)) * " "
            string += "\n"
        return string


    def __getitem__(self, key):
        return self.heat_values[key[0]][key[1]]

    def __setitem__(self, key, value):
        self.heat_values[key[0]][key[1]] = value

    def export_lines(self):
        x_vals = []
        t_vals = []
        vals = []
        for x_index in range(0, self.number_of_x_nodes):
            for t_index in range(0,self.number_of_t_values):
                x_vals.append(self.x_bounds[0] + x_index*self.dx)
                t_vals.append(self.t_bounds[0] + t_index * self.dtau)
                vals.append(self[x_index,t_index])
        return x_vals,t_vals,vals

    def export_plot_lines(self):
        x,y = np.meshgrid(self.S_values, self.t_values)
        z = np.transpose(np.array(self.true_values))
        return x,y,z

    def export_error_plot_lines(self):
        x,y = np.meshgrid(self.S_values, self.t_values)
        z = np.transpose( np.array(self.errors))
        return x,y,z


    def get_stencil_weights(self, stencil_offsets, derivative):
        rows = []
        for i in range(len(stencil_offsets)):
            rows.append([x ** i for x in stencil_offsets])
        equation_matrix = np.matrix(rows)
        # print(equation_matrix)

        delta_vector = [int(i==derivative) * np.math.factorial(derivative) for i in range(len(stencil_offsets))]

        return np.linalg.solve(equation_matrix,delta_vector)

    def solve_full_explicit(self):
        print(self)
        print(self.dx,self.dtau)
        for t_index in range(0, self.number_of_t_values - 1):
            t_weights = self.get_stencil_weights(range(-1 * t_index, 2), 1)
            print("t_weights", t_weights)
            final_t_weight = t_weights[-1]
            for x_index in range(1, self.number_of_x_nodes - 1):
                print("-"*10)
                print("for t index",t_index,"and x_index",x_index)
                x_weights = self.get_stencil_weights([x - x_index for x in range(self.number_of_x_nodes)], 2)
                print("x_weights",x_weights)
                u_second_x_derivative = sum([x_weights[i] * self[i,t_index] for i in range(self.number_of_x_nodes)]) / (self.dx ** 2)
                print("x values", [self[i,t_index] for i in range(self.number_of_x_nodes)])
                print("u''(x)",u_second_x_derivative)
                print(u_second_x_derivative*self.dtau,[t_weights[t] * self[x_index, t] for t in range(t_index)],sum_mine([t_weights[t] * self[x_index, t] for t in range(t_index)]))
                cal = u_second_x_derivative*self.dtau - sum_mine([t_weights[t] * self[x_index, t] for t in range(t_index)])
                print("cal",cal)
                #cal = sum([x_weights[i] * self[i,t_index] for i in range(self.number_of_x_values)]) * self.dtau / (self.dx ** 2) - sum([t_weights[-2 - t] * self[x_index, t_index - t] for t in range(t_index)])
                self[x_index,t_index + 1] = cal/final_t_weight
            print(self)
    def implicit(self, inversion_type):
        if inversion_type == "numpy":
            matrix_rows = []
            for i in range(self.number_of_x_nodes - 2):
                row = []
                for j in range(self.number_of_x_nodes - 2):
                    if i == j:
                        row.append(1 + 2 * self.alpha)
                    elif abs(i - j) <= 1:
                        row.append(-1 * self.alpha)
                    else:
                        row.append(0)
                matrix_rows.append(row)

            x = np.array(matrix_rows)
            inverse_matrix = np.linalg.inv(x)
            for t_index in range(1, self.number_of_t_values):
                b = [self[x_index,t_index-1] for x_index in range(1, self.number_of_x_nodes - 1)]
                b[0] += self.alpha * self[0, t_index - 1]
                b[-1] += self.alpha * self[-1, t_index - 1]
                #print("x",x)
                #print("b",b)
                next_values = np.matmul(inverse_matrix,b)#np.linalg.solve(x,b)
                for next_values_index in range(len(next_values)):
                    self[next_values_index+1,t_index] = next_values[next_values_index]
                    x = self.x_values[next_values_index+1]
                    E = self.E
                    tau = self.tau_values[t_index]
                    if self.american and next_values[next_values_index] < self.payoff(E*exp(x),E)/E*exp((self.k - 1)*x/2 + (self.k + 1)**2 * tau/4):
                        self[next_values_index + 1, t_index] = self.payoff(E*np.exp(x), E)/E * exp((self.k-1)*x/2 +  (self.k + 1)**2 * tau/4)
        elif inversion_type == "tridiagonal":
            m = Matrix((self.number_of_x_nodes - 2,self.number_of_x_nodes - 2))
            for i in range(self.number_of_x_nodes - 2):
                for j in range(self.number_of_x_nodes - 2):
                    if i == j:
                        m[i,j] = 1 + 2 * self.alpha
                    elif abs(i - j) <= 1:
                        m[i, j] = -1 * self.alpha
            for t_index in range(1, self.number_of_t_values):
                b = [self[x_index, t_index - 1] for x_index in range(1, self.number_of_x_nodes - 1)]
                b[0] += self.alpha * self[0, t_index - 1]
                b[-1] += self.alpha * self[-1, t_index - 1]
                b = Matrix(b)
                b.transpose()
                next_values = tridiagonal_solve(m, b)
                for next_values_index in range(self.number_of_x_nodes - 2):
                    self[next_values_index+1,t_index] = next_values[next_values_index]
    def crank_nicolson(self, inversion_type):
        r = self.alpha
        if inversion_type == "numpy":
            matrix_rows = []
            for i in range(self.number_of_x_nodes - 2):
                row = []
                for j in range(self.number_of_x_nodes - 2):
                    if i == j:
                        row.append(1 + self.alpha)
                    elif abs(i - j) <= 1:
                        row.append(-0.5 * self.alpha)
                    else:
                        row.append(0)
                matrix_rows.append(row)
            x = np.array(matrix_rows)
            inverse_matrix = np.linalg.inv(x)

            for t_index in range(1, self.number_of_t_values):
                b = [(1-r) * self[i,t_index-1] + 0.5 * r * (self[i-1,t_index-1] + self[i+1,t_index-1]) for i in range(1, self.number_of_x_nodes - 1)]
                b[0] += 0.5 * self.alpha * self[0, t_index]
                b[-1] += 0.5 * self.alpha * self[-1, t_index]
                #print("x",x)
                #print("b",b)
                next_values = np.matmul(inverse_matrix,b)#np.linalg.solve(x,b)
                for next_values_index in range(len(next_values)):
                    self[next_values_index+1,t_index] = next_values[next_values_index]
                    x = self.x_values[next_values_index+1]
                    E = self.E
                    tau = self.tau_values[t_index]
                    if self.american and next_values[next_values_index] < self.payoff(E*exp(x),E)/E*exp((self.k - 1)*x/2 + (self.k + 1)**2 * tau/4):
                        self[next_values_index + 1, t_index] = self.payoff(E*np.exp(x), E)/E * exp((self.k-1)*x/2 + (self.k + 1)**2 * tau/4)

        elif inversion_type == "tridiagonal":
            m = Matrix((self.number_of_x_nodes - 2,self.number_of_x_nodes - 2))
            for i in range(self.number_of_x_nodes - 2):
                for j in range(self.number_of_x_nodes - 2):
                    if i == j:
                        m[i,j] = 1 + self.alpha
                    elif abs(i - j) <= 1:
                        m[i, j] = -0.5 * self.alpha
            for t_index in range(1, self.number_of_t_values):
                b = [(1-r) * self[i,t_index-1] + 0.5 * r * (self[i-1,t_index-1] + self[i+1,t_index-1]) for i in range(1, self.number_of_x_nodes - 1)]
                b[0] += 0.5 * self.alpha * self[0, t_index]
                b[-1] += 0.5 * self.alpha * self[-1, t_index]
                b = Matrix(b)
                b.transpose()
                next_values = tridiagonal_solve(m, b)
                for next_values_index in range(self.number_of_x_nodes - 2):
                    self[next_values_index+1,t_index] = next_values[next_values_index]


    def get_FDM_values(self,S,E,T,sigma,r):
        self.T = T
        self.S = S
        self.E = E
        self.sigma = sigma
        self.t = 0
        self.k = r/(0.5*sigma**2)
        self.interest_rate = r
        self.alpha = self.dtau / (self.dx ** 2)



    def get_BSE_values(self):
        self.S_values = [self.E*np.exp(x) for x in self.x_values]
        self.t_values = [self.T - 2*tau/(self.sigma**2) for tau in self.tau_values]
        k = self.k
        for i in range(self.number_of_x_nodes):
            x = self.x_values[i]
            for j in range(self.number_of_t_values):
                tau = self.tau_values[j]
                self.true_values[i][j] = self.E * self.heat_values[i][j] * np.exp((k-1)*-x/2 - (k+1)**2 * tau / 4 )


    def get_value_estimation_at_start(self,S):
        a,b = None,None
        #print("looking for",S)
        for i in range(len(self.S_values) - 1):
            #print("between",self.S_values[i],self.S_values[i+1])
            if self.S_values[i] <= S <= self.S_values[i+1]:
                a = i
                b = i + 1
                break
        #print("between", self.S_values[a], self.S_values[b])
        upper_weight = (S - self.S_values[a])/(self.S_values[b] -  self.S_values[a])
        lower_weight = (self.S_values[b] - S)/(self.S_values[b] -  self.S_values[a])
        return lower_weight*self.true_values[a][-1] + upper_weight*self.true_values[b][-1]


