OVERLOADABLE_OPERATORS = {'init', 'call', 'del', 'repr', 'str', 'unicode', 'nonzero', 'cmp', 'eq', 'ne', 'lt', 'le', 'ge', 'gt', 'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'divmod', 'pow', 'lshift', 'rshift', 'and', 'or', 'xor', 'radd', 'rsub', 'rmul', 'rdiv', 'rfloordiv', 'rmod', 'rdivmod', 'rpow', 'rlshift', 'rrshift', 'rand', 'ror', 'rxor', 'iadd', 'isub', 'imul', 'idiv', 'itruediv', 'ifloordiv', 'imod', 'ipow', 'ilshift', 'irshift', 'iand', 'ior', 'ixor', 'neg', 'pos', 'invert', 'abs', 'float', 'hex', 'int', 'long', 'oct', 'index', 'complex', 'len', 'contains', 'iter', 'reversed', 'getitem', 'setitem', 'delitem', 'getslice', 'setslice', 'delslice', 'getattr', 'getattribute', 'setattr', 'delattr', 'hash', 'get', 'set', 'delete', 'getstate', 'setstate', 'getinitargs', 'getnewargs', 'reduce', 'reduce_ex', 'newobj', 'copy', 'deepcopy', 'enter', 'exit', 'new', 'coerce', 'subclasses', 'dict', 'vars', 'class', 'metaclass', 'bases', 'name', 'slots', 'weakref', 'doc', 'file', 'import', 'builtins', 'all', 'builtin', 'main', 'future', 'requires', 'traceback_hide', 'debug'}
OVERLOADABLE_BINARY_OPERATORS = {'cmp', 'eq', 'ne', 'lt', 'le', 'ge', 'gt', 'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'divmod', 'pow', 'lshift', 'rshift', 'and', 'or', 'xor'}
UNSAFE_OVERLOADABLE_OPERATORS = {'init', 'getattr', 'getattribute', 'debug', 'newobj'}
SAFE_OVERLOADABLE_OPERATORS = OVERLOADABLE_BINARY_OPERATORS.union({'call', 'len'})

'''
This is a class designed to allow an operation to apply to every element of a user-defined container.

A class 'C' that wants to use this must meet a few requirements:
    - It must be iterable
    - It must be subscriptable
    - It be able to accept a list as the only argument for a call to its constructor

To enable the usage of the elementwise operation for a class, define the __getattr__ method for the class if there wasn't any, make sure that __getattr__(self, 'e')
returns elementWise(self). For example, the following definition would suffice:

def __getattr__(self, attr):
    if attr == 'e':
        return elementWise(self)
    raise AttributeError("'" + self.__class__.__name__ + "' object has no attribute '" + attr + "'")

This class currently works for all binary operators, __call__, and any user-defined methods defined for all the iterates of the instance being
operated over. It only works for positional arguments.
'''

class elementWise:
    def __init__(self, Iter):
        self.type = type(Iter)
        self.elems = list(Iter)

    def tryFunc(element, method, pos, *posargs):
        if len(posargs) == 0:
            try:
                returnVal = eval('element.e.' + method + '()')
                if returnVal == NotImplemented:
                    raise Exception('NotImplemented')
            except:
                returnVal = eval('element.' + method + '()')
                if returnVal == NotImplemented:
                    raise Exception('NotImplemented')
        else:
            arg1 = posargs[0]
            posArgs = list(posargs)
            posArgs.pop(0)
            try:
                returnVal = eval('element.e.' + method + '(arg1[pos], *posArgs)')
                if returnVal == NotImplemented:
                    raise Exception('NotImplemented')
            except:
                try:
                    returnVal = eval('element.e.' + method + '(arg1, *posArgs)')
                    if returnVal == NotImplemented:
                        raise Exception('NotImplemented')
                except:
                    try:
                        returnVal = eval('element.' + method + '(arg1[pos], *posArgs)')
                        if returnVal == NotImplemented:
                            raise Exception('NotImplemented')
                    except:
                        try:
                            newMethod = method.lstrip('_')
                            returnVal = eval('arg1[pos].__r' + newMethod + '(element)')
                            if returnVal == NotImplemented:
                                raise Exception('NotImplemented')
                        except:
                            try:
                                returnVal = eval('element.' + method + '(arg1, *posArgs)')
                                if returnVal == NotImplemented:
                                    raise Exception('NotImplemented')
                            except:
                                newMethod = method.lstrip('_')
                                returnVal = eval('arg1.__r' + newMethod + '(element)')
                                if returnVal == NotImplemented:
                                    raise Exception('NotImplemented')
        return returnVal

    def curry(self, method):
        returnList = [lambda x, elem=elem : lambda *posArgs : elementWise.tryFunc(elem, method, i, *([x] + list(posArgs))) for i, elem in enumerate(self.elems)]
        return self.type(returnList).e

    def __getattr__(self, attr):
        def func(*posArgs):
            if len(posArgs) <= 1:
                returnList = [elementWise.tryFunc(elem, attr, i, *posArgs) for i, elem in enumerate(self.elems)]
                return self.type(returnList)
            else:
                posArgsList = list(posArgs)
                arg1 = posArgsList.pop(0)
                return self.curry(attr)(arg1).e(*posArgsList)
        return func

    for operatorName in SAFE_OVERLOADABLE_OPERATORS:
        try:
            exec('''def __''' + operatorName + '''__(self, *posArgs):
    method = self.__getattr__(''' + "'__" + operatorName +  "__'" + ''')
    return method(*posArgs)''')
        except Exception as err:
            print(err)
            print(operatorName)
