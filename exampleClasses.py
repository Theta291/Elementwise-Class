from elementwise import *
import string

@initInstDesc.createDesc('o')
class outerProd:
    def __init__(self, vec):
        self.vec = vec

    def __mul__(self, vec2):
        return matrix(self.vec.e * vec2.e)

@elementWise.addDesc
class vector:
    def __init__(self, Iter):
        self.list = list(Iter)

    def __getitem__(self, key):
        return self.list[key]

    def append(self, elem):
        self.list.append(elem)

    def __iter__(self):
        return iter(self.list)

    def __len__(self):
        return len(self.list)

    def mag(self):
        return (self * self) ** 0.5

    def __str__(self):
        return '<' + ''.join([str(elem) + ', ' for i, elem in enumerate(self.list[:-1])]) + str(self.list[-1]) + '>'

    def __add__(self, other):
        return self.e + other

    def __mul__(self, other):
        if type(other) is vector:
            return sum(self.e * other)
        else:
            return NotImplemented
            #return self.e * other

    def __rmul__(self, other):
        return self * other
    
    def __eq__(self, other):
        if type(other) is vector:
            return self.list == other.list
        else:
            return False

@elementWise.addDesc
class matrix:
    def __init__(self, Iter):
        self.vec = vector([vector(elem) for elem in Iter])

    def __getattr__(self, attr):
        if attr == 'T':
            newVec = vector([vector(()) for i in range(self.width())])
            for row in self.vec:
                for i, entry in enumerate(row):
                    newVec[i].append(entry)
            return matrix(newVec)
        else:
            raise AttributeError("Matrix class has no attribute:", attr)

    def __getitem__(self, key):
        return self.vec[key]

    def height(self):
        return len(self.vec)

    def width(self):
        return len(self.vec[0])

    def __iter__(self):
        return iter(self.vec)

    def __str__(self):
        retStr = '<\n'
        for row in self.vec:
            retStr += ' ' + str(row) + '\n'
        retStr += '>'
        return retStr

    def __add__(self, other):
        return self.e + other

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if type(other) is matrix:
            return matrix(self.vec.e(depth=1) * other.T.vec.e(depth=1))
        elif type(other) is vector:
            newOther = matrix([other]).T
            return self * newOther
        else:
            return self.vec.e * other

    def inv(self):
        n = self.height()
        returnMat = matrix(self)
        for k in range(n):
            newMat = matrix(returnMat)
        return NotImplemented
