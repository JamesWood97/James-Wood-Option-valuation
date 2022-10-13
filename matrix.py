import random, time
from math import *
import matplotlib.pyplot as plt
class Matrix:
    def __init__(self,n,mathematical_indexing=False):
        self.index_offset = 0
        if type(n) is int:
            self.values = [[0 for i in range(n)] for j in range(n)]
            self.size = (n,n)
        elif type(n) is tuple:
            self.values = [[0 for i in range(n[1])] for j in range(n[0])]
            self.size = (n[0],n[1])

        elif type(n) is list:
            self.values = [n]
            self.size = (1,len(n))

        elif type(n) == Matrix:
            self.size = n.size
            self.values = [[0 for i in range( self.size[1] )] for j in range( self.size[0] )]
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    self[i,j] = n[i,j]

        elif type(n) is str:
            row_strings = n.split(";")
            size_1 = len(row_strings)
            self.values = [[0 for i in range(size_1)] for j in range(size_1)]
            for row_index, row_string in enumerate(row_strings):
                if row_string[0] == " ":
                    row_string = row_string[1:]
                vals = [float(x) for x in row_string.replace(","," ").split(" ")]
                size_0 = len(vals)
                for j in range(len(vals)):
                    self[row_index,j] = vals[j]
            self.size = (size_0,size_1)

        self.mathematical_indexing = mathematical_indexing
        self.index_offset = int(self.mathematical_indexing)

    def __getitem__(self, key):
        if type(key) is int and self.size[1] == 1:
            return self.values[key - self.index_offset][0]
        elif type(key) is int and self.size[0] == 1:
            return self.values[0][key - self.index_offset]
        else:
            return self.values[key[0] - self.index_offset][key[1] - self.index_offset]
    def __setitem__(self, key, value):
        if type(key) is int and self.size[1] == 1:
            self.values[key - self.index_offset][0] = value
        elif type(key) is int and self.size[0] == 1:
            self.values[0][key - self.index_offset] = value
        else:
            self.values[key[0] - self.index_offset][key[1] - self.index_offset] = value

    def __repr__(self):
        self.index_offset = 0

        string = ""
        for i in range( self.size[0] ):
            row = ""
            for j in range( self.size[1] ):
                label_size = 9
                val = str(round(self[i,j],6))
                if len(val) > label_size:
                    val = val[0:label_size]
                val = (label_size - len(val)) * " " + val
                row += val + " "
            string += row + "\n"

        self.reset_indexing()
        return string

    def __add__(self, other):
        self.index_offset = 0
        other.index_offset = 0
        new_matrix = Matrix(self.size)
        if other.size != self.size:
            raise Exception(
            )
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                new_matrix[i, j] = self[i,j] + other[i,j]
        other.reset_indexing()
        self.reset_indexing()
        return new_matrix

    def __sub__(self, other):
        self.index_offset = 0
        other.index_offset = 0
        new_matrix = Matrix(self.size)
        if other.size != self.size:
            raise Exception(
            )
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                new_matrix[i, j] = self[i,j] - other[i,j]
        other.reset_indexing()
        self.reset_indexing()
        return new_matrix


    def __mul__(self, other):
        self.index_offset = 0
        if type(other) == Matrix:

            if other.size[0] != self.size[1]:
                raise Exception("Can only multiply matricies of the same size!")
            new_matrix = Matrix((self.size[0],other.size[1]))
            other.index_offset = 0
            for i in range(new_matrix.size[0]):
                for j in range(new_matrix.size[1]):
                    new_matrix[i,j] = sum([self[i,k] * other[k,j] for k in range(self.size[1])])
            other.reset_indexing()
        else:
            new_matrix = Matrix(self.size)
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    new_matrix[i,j] = self[i,j] * other
        self.reset_indexing()
        return new_matrix



    def idehtity(self):
        self.index_offset = 0
        n = min(self.size)

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self[i,j] = int(i==j)
        self.index_offset = int(self.mathematical_indexing)

    def row_operation(self,row_index,row_to_add_from,multiplier=1):
        for i in range(self.size[0]):
            self[i,row_index] += self[i,row_to_add_from] * multiplier

    def multiply_row(self,row_index,multiplier):
        for i in range(self.size[0]):
            self[i, row_index] *= multiplier

    def sum_row(self,row_index):
        return sum(self.values[row_index])



    def invert(self):
        if self.size[0] != self.size[1]:
            raise Exception()
        self.index_offset = 0
        n = self.size[0]
        old_values = [[self.values[i][j] for j in range(len(self.values[i]))] for i in range(len(self.values))]#make a copy of the values
        inverted_matrix = Matrix(n,mathematical_indexing=False)
        inverted_matrix.idehtity()

         #print(self)
        #print(inverted_matrix)
        #print("lower left")
        for column_index in range(n-1):
            for row_index in range(column_index+1,n):
                #print("fixing",column_index,row_index)
                multiplier = -1 * self[column_index,row_index] / self[column_index,column_index]
                #print("multiplier",multiplier)
                self.row_operation(row_index,column_index,multiplier)
                inverted_matrix.row_operation(row_index,column_index,multiplier)
                #print(self)
                #print(inverted_matrix)

        #print("-"*10)
        #print("upper right")
        for column_index in range(n-1,0,-1):
            for row_index in range(column_index-1,-1,-1):
                #print("fixing",column_index,row_index)
                multiplier = -1 * self[column_index,row_index] / self[column_index,column_index]
                #print("multiplier",multiplier)
                self.row_operation(row_index,column_index,multiplier)
                inverted_matrix.row_operation(row_index,column_index,multiplier)
                #print(self)
                #print(inverted_matrix)
        #print("dividing rows")
        for i in range(n):
            #print("row",i)
            inverted_matrix.multiply_row(i,1/self[i,i])
            self.multiply_row(i,1/self[i,i])
            #print(self)
            #print(inverted_matrix)
        #print("done!")
        #print(self)
        self.reset_indexing()
        self.values = old_values
        return inverted_matrix


    def get_diagonals(self):
        self.index_offset = 0
        a = []
        b = []
        c = []
        for i in range(min(self.size) - 1):
            a.append(self[i,i])
            b.append(self[i+1,i])
            c.append(self[i,i+1])
        a.append(self[-1,-1])
        self.reset_indexing()
        return a,b,c

    def get_diagonals(self):
        self.index_offset = 0
        a = []
        b = []
        c = []
        for i in range(min(self.size) - 1):
            a.append(self[i+1,i])
            b.append(self[i, i])
            c.append(self[i,i+1])
        b.append(self[-1,-1])
        self.reset_indexing()
        return a,b,c

    def invert_tridiagonal(self):
        self.index_offset = 1
        a,b,c = self.get_diagonals_old()
        a = [None] + a##
        b = [None] + b##so the lists start at one instead of 0 (makes programming easier)
        c = [None] + c##
        theta = [1,self[0,0]]
        phi = [None]*self.size[0] + [a[-1],1]
        for i in range(2,self.size[0]+1):
            theta.append(theta[i-1] * a[i] - theta[i-2]*b[i-1]*c[i-1])
            i = self.size[0] - i + 1
            phi[i] = a[i] * phi[i+1] - b[i]*c[i] * phi[i+2]
        inverted_matrix = Matrix(self.size,mathematical_indexing=True)
        for i in range(1,self.size[0]+1):
            for j in range(1,self.size[1]+1):
                if i == j:
                    inverted_matrix[i,j] = theta[i-1]*phi[j+1] / theta[self.size[0]]
                elif i < j:
                    inverted_matrix[i, j] = (-1)**(i+j) * theta[i - 1] * phi[j + 1] / theta[self.size[0]]
                    for x in range(i,j):
                        inverted_matrix[i, j] *= b[x]
                elif i > j:
                    inverted_matrix[i, j] = (-1)**(i+j) * theta[j - 1] * phi[i + 1] / theta[self.size[0]]
                    for x in range(j,i):
                        inverted_matrix[i, j] *= c[x]




        self.reset_indexing()
        inverted_matrix.transpose()
        return inverted_matrix

    def random_tridiangonal(self):
        self.index_offset = 0
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if abs(i-j) < 2:
                    self[i,j] = random.randint(-10,10)
                    if self[i,j] == 0:
                        self[i,j] = 1
                else:
                    self[i,j] = 0
        self.reset_indexing()

    def reset_indexing(self):
        self.index_offset = int(self.mathematical_indexing)

    def random(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self[i+self.index_offset,j+self.index_offset] = random.randint(1,20)

    def transpose(self):
        new_values = [[0 for i in range(self.size[0])] for j in range(self.size[1])]
        for i in range(self.index_offset,self.size[0] + self.index_offset):
            for j in range(self.index_offset, self.size[1] + self.index_offset):
                new_values[j - self.index_offset][i - self.index_offset] = self[i, j]
        self.size = (self.size[1],self.size[0])
        self.values = new_values

    def get_L_matrix(self,column):
        L_matrix = Matrix(self.size)
        L_matrix.idehtity()
        for i in range(column+self.index_offset+1,self.size[0]+self.index_offset):
            L_matrix[i,column] = -1 * (self[i,column]/self[column,column])
        return L_matrix

    def get_LU_matricies(self):
        id = Matrix(self.size)
        id.idehtity()
        A_i = Matrix(self)
        L = Matrix(self.size)
        L.idehtity()
        for i in range(self.size[0]):
            l_i = A_i.get_L_matrix(i)
            L = L * l_i
            A_i = l_i * A_i
            #print("L_",i)
            #print(L)

        return L* -1 + id + id, A_i


    def get_chomsky_decomp(self):
        n = self.size[0]
        L = Matrix(n)
        for i in range(n):
            for j in range(i+1):
                print(i,j)
                if i != j:
                    L[i,j] =1/L[j,j] * (self[i,j] - sum([L[i,k]*L[j,k] for k in range(j)]))
                elif i == j and i != 0:
                    L[i,j] = (self[i,j] - sum([L[j,k]**2 for k in range(j)]))**0.5
                else:
                    L[i,j] = self[i,j]**0.5
        return L

def solve(A,b):
    return A.invert()*b

def LU_solve(A,b):
    L,U = A.get_LU_matricies()
    y = []
    x = [None for i in range(A.size[0])]
    for n in range(A.size[0]):
        y.append(b[n] - sum([L[n,i] * y[i] for i in range(n)]))
    for n in range(A.size[0]-1,-1,-1):
        x[n] = (y[n] - sum([U[n,i]*x[i] for i in range(n+1,A.size[0])]))/U[n,n]
    x = Matrix(x)
    x.transpose()
    return x

def solve_with_iter(A,b,n=300):
    Ainv = A.invert()
    Ainv = newton_interation(Ainv,A,n)
    return Ainv*b

def tridiagonal_solve(A,d):
    n = A.size[0]
    a,b,c = A.get_diagonals()
    a = [None] + a
    c.append(None)
    d = Matrix(d)
    #print(a)
    #print(b)
    #print(c)
    for i in range(1,n):
        #print("i:",i)
        w = a[i]/b[i-1]
        #print(w)
        b[i] = b[i] - w*c[i-1]
        d[i] = d[i] - w*d[i-1]
        #print(b)
        #print(d)
    x = [None for i in range(n)]
    x[-1] = d[n-1]/b[n-1]
    for i in range(n-2,-1,-1):
        #print("i",i,"x",x)
        x[i] = (d[i] - c[i]*x[i+1])/b[i]
    """a = [None] + a
    print(a,b,c)
    cdash = [c[0]/b[0]]
    for i in range(1, n - 1):
        cdash.append(c[i]/(b[i] - a[i]*cdash[i-1]))
    ddash = [d[1] / b[1]]
    for i in range(1, n):
        ddash.append((d[i] - a[i]*ddash[i-1])/(b[i] - a[i]*cdash[i-1]))
    print(cdash)
    print(ddash)
    x = [None for i in range(n)]
    x[-1] = ddash[-1]
    for i in range(n-2,-1,-1):
        x[i] = ddash[i] - cdash[i] * x[i+1]"""
    x = Matrix(x)
    x.transpose()
    return x

def newton_interation(inv_A_est,A,amount_of_interations=30):
    id = Matrix(A)
    id.idehtity()
    for i in range(amount_of_interations):
        inv_A_est = inv_A_est*2 - inv_A_est*(A*inv_A_est)
    return inv_A_est

if __name__ == "__main__":
    M = Matrix("4 12 -16; 12 37 -43; -16 -43 98")
    print(M)
    L = M.get_chomsky_decomp()
    print(L)
    L_trans = Matrix(L)
    L_trans.transpose()
    print(L*L_trans)
    input()











    n = 10
    random.seed(4)
    A = Matrix(n)
    A.random_tridiangonal()
    b = Matrix((n,1))
    b.random()
    x = tridiagonal_solve(A,b)
    print(x)
    print(b[3])
    b = A*x
    print(b[3])



    n_vals = []
    LU_vals = []
    gaus_vals = []
    tri_vals = []
    trials = 10
    max_n = 100
    min_n = 20
    for _ in range(1):
        for n in range(min_n,max_n + 1):
            random.seed(4)
            A = Matrix(n)
            A.random_tridiangonal()
            b = Matrix((n, 1))
            b.random()
            LU_vals_trials = []
            gaus_vals_trials = []
            tri_vals_trails = []
            for i in range(trials):
                print(n,i)
                time1 = time.process_time_ns()
                x = LU_solve(A,b)
                time2 = time.process_time_ns()
                x = solve(A,b)
                time3 = time.process_time_ns()
                x = tridiagonal_solve(A, b)
                time4 = time.process_time_ns()
                LU_vals_trials.append(log((time2 - time1 + 1)/1000000,  2))
                gaus_vals_trials.append(log((time3 - time2+ 1)/1000000,2))
                tri_vals_trails.append(log((time4 - time3+ 1)/1000000, 2))
            LU_vals_trials.sort()
            gaus_vals_trials.sort()
            tri_vals_trails.sort()
            LU_vals_trials = LU_vals_trials[1:-1]
            gaus_vals_trials = gaus_vals_trials[1:-1]
            tri_vals_trails = tri_vals_trails[1:-1]
            LU_vals.append(sum(LU_vals_trials)/len(LU_vals_trials))
            gaus_vals.append(sum(gaus_vals_trials) / len(gaus_vals_trials))
            tri_vals.append(sum(tri_vals_trails) / len(tri_vals_trails))
            n_vals.append(n)


    plt.plot(n_vals, gaus_vals, label="Gaussian Elimination")
    plt.plot(n_vals, LU_vals, label="LU Decomposition")
    #plt.plot(n_vals, tri_vals, label="Tridiagonal")
    plt.xlabel("size of square matrix")
    plt.ylabel("log base 2 of the time taken in ms")
    plt.legend(loc='upper right')
    plt.show()