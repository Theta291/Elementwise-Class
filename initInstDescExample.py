from elementwise import *
import exampleClasses

#This file implements an outer product descriptor using the initInstDesc class, and has a walkthrough in the comments.

'''The outer product of two vectors returns a matrix which is a table of the products of every possible pair containing one component from each vector.

initInstDesc work on 'operator classes', which are classes that should be used to change the functionality of existing methods for a class.
However, the only strict requirement for initInstDesc to work on an operator class is that the class must be able to accept an instance of another class as the only argument to its constructor.
'''

#Before implementing the functionality of the outer product, we use the 'initInstDesc.createDesc' wrapper with the argument 'o', so we can eventually take an outer product like 'vec1.o * vec2'.
@initInstDesc.createDesc('o')
class outerProd:
    #To take an outer product, we only need to know the first factor in the product.
    def __init__(self, vec):
        self.vec = vec

    #An outer product is simply a cartesian product of the arguments, then a distribution of the multiplication operation.
    #We can implement that using elementwise, like this:
    def __mul__(self, vec2):
        return exampleClasses.matrix(self.vec.e * vec2.e)

#To make sure we can use the 'o' descriptor, we use the automatically generated wrapper 'outerProd.addDesc'.
@outerProd.addDesc
class vector(exampleClasses.vector):
    pass
