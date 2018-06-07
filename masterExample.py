import elemWise
import string
import random

@elemWise.initInstDesc.createDesc('o')
class outerProd:
    def __init__(self, vec):
        self.vec = vec

    def __mul__(self, vec2):
        return matrix(self.vec.e * vec2.e)

@outerProd.addDesc
@elemWise.elementWise.addDesc
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

@elemWise.elementWise.addDesc
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

vec1 = vector((1, 2, 3))
vec2 = vector((4, 5, 6))
vec3 = vector((7, 8, 9))
vec4 = vector((10, 11, 12))
mat1 = matrix((vec1, vec2))
mat2 = matrix((vec3, vec4))
mat2 = mat2.T
print('basic test of elementWise')
print(vec1.e * vec2)
print('test of cartesian elementWise')
print(vec1.e * vec2.e)
print('test of elementWise on iterable of depth 2')
print(vector((vec1, vec2)).e * vector((vec3, vec4)))
print('test of cartesian elementWise on iterables of depth 2')
print(vector((vec1, vec2)).e * vector((vec3, vec4)).e)
print('test of multiple arg processing')
tripAdd = lambda x, y, z : x + y + z
tripAdd = elemWise.elementWise.process(tripAdd)
print(tripAdd(vec1.e, vec2.e, vec3.e))
print('test of depth restricted elementWise')
print(vec1.e(depth = 0) * vec2.e(depth = 0))
print('test of matrix multiplication')
print(mat1 * mat2)
kwArgMul = lambda param1=None, param2=None : param1 * param2
print('test of keyword arg processing with regular arguments')
print(elemWise.elementWise.process(kwArgMul)(param1=1, param2=2))
print('test of keyword arg processing with elementWise arguments')
print(elemWise.elementWise.process(kwArgMul)(param1=vec1.e, param2=vec2.e))

print('test of outerProd')
print(vec1.o * vec2)

print('regression example')
firstPower = lambda x : x ** 1
secondPower = lambda x : x ** 2
thirdPower = lambda x : x ** 3
twoToThe = lambda x : 2 ** x
testFeatures = vector((firstPower, secondPower, thirdPower, twoToThe))
sampleIn = vector((1, 2, 3, 4))
sampleOut = vector([random.gauss(0, 1) for i in range(4)])
featureMat = matrix(testFeatures.e(sampleIn.e)).T
print(featureMat)
