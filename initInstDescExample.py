import elemWise
import exampleClasses

@elemWise.initInstDesc.createDesc('o')
class outerProd:
    def __init__(self, vec):
        self.vec = vec

    def __mul__(self, vec2):
        return exampleClasses.matrix(self.vec.e * vec2.e)
        
vec1 = exampleClasses.vector((1, 2, 3))
vec2 = exampleClasses.vector((4, 5, 6))
print('test of outerProd')
print(vec1.o * vec2)
