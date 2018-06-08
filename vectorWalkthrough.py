from elementwise import *
import string

#This file implements a vector class using the elementwise module, and has a walkthrough for it in the comments.

'''Consider creating a class to implement vectors, including the following properties of vectors:
    - Vector addition
    - Scalar/vector multiplication
    - Cross-products
    - Magnitude of a vector
We also want this added functionality, for ease of use:
    - Display the components of a vector
    
We will implement these properties using the elementWise class'''

'''First, to make sure the elementWise class can be used with our vector class, we have to meet the requirements
    1. The vector class must be able to accept a single list as the only argument to its constructor.
    2. The vector class must have an '__iter__' method.
    3. The vector class must have a '__getitem__' method.
    4. The vector class must have a '__len__' method.
'''

#But before that, we use the 'elementWise.addDesc' wrapper so we can do elementwise operations:
@elementWise.addDesc
class vector:
    
    #1. The vector class must be able to accept a single list as the only argument to its constructor.
    #We just take the List and copy its elements to use as the components of our vector.
    def __init__(self, List):
        self.comps = list(List)

    #2. The vector class must have an '__iter__' method.
    #We just iterate over the components.
    def __iter__(self):
        return iter(self.comps)

    #3. The vector class must have a '__getitem__' method.
    #We return the proper component from our list of components.
    def __getitem__(self, n):
        return self.comps[n]

    #4. The vector class must have a '__len__' method.
    #We return the number of components, which is the length of our list of components.
    def __len__(self):
        return len(self.comps)

    #Now we can use the elementWise operator to implement the vector properties.
    #The first is vector addition. We just want to add the components of one vector to another, so we use the operator like this:
    def __add__(self, vec2):
        return self.e + vec2

    #The next two properties, scalar multiplication and cross products, both use the same operator, '*'.
    def __mul__(self, other):
        #The vector cross product only applies to the case where we 'multiply' two vectors together.
        if type(other) is vector:
            #It is the sum of the elementwise multiplication of the vectors, so we implement it like this:
            return sum(self.e * other)
        else:
            #If we aren't multiplying two vectors together, we just attempt scalar multiplication.
            #If we call the elementwise operator of an iterable along with a non-iterable, every element of the iterable is called with the non-iterable, which is what we want.
            return self.e * other

    #The last property of a vector we need to implement is magnitude.
    #The cross product of a vector with itself is simply the magnitude squared, so we write:
    def mag(self):
        return (self * self) ** 0.5

    #Lastly, we want to return a string of the vector, which incorporates the string of every component of the vector.
    #We will implement the notation that uses a comma separated list and '<' and '>' as brackets.

    #To be honest, the easiest implementation uses a simple list comprehension, slicing, and the string library '.join' method:
    def __str__(self):
        return '<' + ''.join([str(comp) + ', ' for comp in self[:-1]]) + str(self[-1]) + '>'

    #Here is a walkthrough of why is it difficult to use the elementWise class to do this:
    #Main focus in this implementation is to replace the list comprehension used in the previous definition. We may attempt something like this:
    def __str__(self):
        return '<' + ''.join((str(self[:-1].e)).e + ', ') + str(self[-1]) + '>'
    #Notice that we have to use '.e' twice, because, theoretically, 'str(self[:-1].e)' should return a vector with the strings of the components, and we need to add the string ', ' to every component.

    #To test our '__str__' method, we attempt this line of code 'print(vector([4, 5, 6]))'.
    strTest = 'print(vector([4, 5, 6]))'
    #So whenever we want to run a test, we run 'exec(vector.strTest)'.

    #When we try to run 'exec(vector.strTest)', this error is raised:
    "AttributeError: 'list' object has no attribute 'e'"

    #This is because the descriptor we use, 'e', for our elementwise operator is applied to each class we want to use it with manually, using the 'elementWise.addDesc' wrapper.
    #This wrapper edits our user-defined class so we can use the elementwise operator by trying to access the attribute 'e'.
    #However, we didn't wrap the class 'list', and we can't wrap it, because we can't edit built-in classes.
    #This becomes a problem when we need to get a slice of a vector. By default, slicing returns lists.

    #To try to get around this, we can manually call the constructor, like this:
    def __str__(self):
        return '<' + ''.join(elementWise((str(elementWise(self[:-1])))) + ', ') + str(self[-1]) + '>'
    #With this attempt, our syntax starts to get less sugary.

    #We test it, and it raises this error:
    "TypeError: __str__ returned non-string (type list)"

    #This was caused by the type checking on the built in function 'str'. 'str' checks its return value to make sure that its a string, even when it is overloaded otherwise.
    #However, we can attempt to get around this by called the '__str__' method directly:
    def __str__(self):
        return '<' + ''.join(elementWise((elementWise(self[:-1]).__str__())) + ', ') + str(self[-1]) + '>'
    #Our syntax is now even uglier.

    #We test it again, and this time it doesn't raise an error. Instead, it returns this:
    '<4,5 6>'

    #This isn't what we wanted either! Why does this happen?
    #The way that elementWise matches the elements of one instance with the elements of another is that it checks the size of both instances, and if they are the same size, it matches the elements pairwise.
    #In this case, the instances are the first 2 components of the vector (4 and 5) and the 2 characters in the string (',' and ' ').
    #Because the length is the same, '4' is matched with ',' and '5' is matched with ' '.

    #Luckily, elementWise has just the thing for this situation: the depth parameter in its constructor.
    #We don't want to access the elements of ', ', so we try to use the elementWise operators with depth 0:
    def __str__(self):
        return '<' + ''.join(elementWise((elementWise(self[:-1]).__str__())) + elementWise(', ', depth=0)) + str(self[-1]) + '>'

    #This time, our test prints this:
    "<4[',', ' ']5[',', ' ']6>"

    #Also not what we want. This is because the string type doesn't meet the requirements for elementWise to support it (at least not in the way we want it to).
    #It can't cast a list of characters into a larger string. Therefore, the string cast of it is "[',', ' ']".

    #To avoid this, we can try making a function which both converts something to a string and then adds the ', '. We can process this function using elementWise and call it.
    def __str__(self):
        @elementWise.process
        def tempFunc(x):
            return str(x) + ', '
        return '<' + ''.join(tempFunc(elementWise(self[:-1]))) + str(self[-1]) + '>'

    #Finally, when we run our test, it prints the proper string:
    "<4, 5, 6>"
    
    #This whole process highlights many of the problems with using elementWise.
    #Even though it was possible to use elementWise, the job of the class is to make syntax more easy, which it did not do in this case.
