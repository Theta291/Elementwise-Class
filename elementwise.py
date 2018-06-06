OVERLOADABLE_OPERATORS = {'init', 'call', 'del', 'repr', 'str', 'unicode', 'nonzero', 'cmp', 'eq', 'ne', 'lt', 'le', 'ge', 'gt', 'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'divmod', 'pow', 'lshift', 'rshift', 'and', 'or', 'xor', 'radd', 'rsub', 'rmul', 'rdiv', 'rfloordiv', 'rmod', 'rdivmod', 'rpow', 'rlshift', 'rrshift', 'rand', 'ror', 'rxor', 'iadd', 'isub', 'imul', 'idiv', 'itruediv', 'ifloordiv', 'imod', 'ipow', 'ilshift', 'irshift', 'iand', 'ior', 'ixor', 'neg', 'pos', 'invert', 'abs', 'float', 'hex', 'int', 'long', 'oct', 'index', 'complex', 'len', 'contains', 'iter', 'reversed', 'getitem', 'setitem', 'delitem', 'getslice', 'setslice', 'delslice', 'getattr', 'getattribute', 'setattr', 'delattr', 'hash', 'get', 'set', 'delete', 'getstate', 'setstate', 'getinitargs', 'getnewargs', 'reduce', 'reduce_ex', 'newobj', 'copy', 'deepcopy', 'enter', 'exit', 'new', 'coerce', 'subclasses', 'dict', 'vars', 'class', 'metaclass', 'bases', 'name', 'slots', 'weakref', 'doc', 'file', 'import', 'builtins', 'all', 'builtin', 'main', 'future', 'requires', 'traceback_hide', 'debug'}

OVERLOADABLE_BINARY_OPERATORS = {'cmp', 'eq', 'ne', 'lt', 'le', 'ge', 'gt', 'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'divmod', 'pow', 'lshift', 'rshift', 'and', 'or', 'xor'}
REVERSED_BINARY_OPERATORS = {'r' + elem for elem in OVERLOADABLE_BINARY_OPERATORS}

SAFE_OVERLOADABLE_OPERATORS = OVERLOADABLE_BINARY_OPERATORS.union({'call'})
SAFE_OVERLOADABLE_OPERATORS.update(REVERSED_BINARY_OPERATORS)

UNSAFE_OVERLOADABLE_OPERATORS = {'init', 'getattr', 'debug'}
#SAFE_OVERLOADABLE_OPERATORS = OVERLOADABLE_OPERATORS - UNSAFE_OVERLOADABLE_OPERATORS

'''
This is a class designed to allow an operation to apply to every element of a user-defined container.

A class 'C' that wants to use this must meet a few requirements:
    - It must be iterable
    - It must be subscriptable
    - It must be able to accept a list as the only argument for a call to its constructor

To enable the usage of the elementwise operation for a class, add the wrapper '@elementWise.addDesc' to the beginning of the class definition.

This class currently works for all binary operators, __call__, and any user-defined methods defined for all the iterates of the instance being
operated over. It only works for positional arguments.
'''

class initInstDesc:
    def __init__(self, cls, *posArgs):
        if len(posArgs) == 0:
            self.initKwParams = {}
        else:
            self.initKwParams = posArgs[0]
        self.retClass = cls

    def __get__(self, inst, instType=None):
        return self.retClass(inst, **self.initKwParams)

    def createDesc(name, *posArgs):
        if len(posArgs) == 0:
            kwParamDefaults = {}
        else:
            kwParamDefaults = posArgs[0]
        def subWrap(cls):
            initCopy = cls.__init__
            def init(self, origInst, *posArgs, **kwArgs):
                self.orig = origInst
                initCopy(self, origInst, *posArgs, **kwArgs)
            cls.__init__ = init
            if hasattr(cls, 'addDesc'):
                addDescCopy = cls.addDesc
                def addDesc(otherCls):
                    setattr(otherCls, name, initInstDesc(cls, kwParamDefaults))
                    return addDescCopy(otherCls)
            else:
                def addDesc(otherCls):
                    setattr(otherCls, name, initInstDesc(cls, kwParamDefaults))
                    return otherCls
            cls.addDesc = addDesc
            if hasattr(cls, '__call__'):
                callCopy = cls.__call__
                def newCall(self, *posArgs, **kwArgs):
                    if set(kwArgs.keys()).issubset(set(kwParamDefaults.keys())) and len(posArgs) == 0:
                        newDict = dict(kwParamDefaults)
                        newDict.update(kwArgs)
                        return cls(self.orig, **kwArgs)
                    else:
                        return callCopy(self, *posArgs, **kwArgs)
            else:
                def newCall(self, *posArgs, **kwArgs):
                    if set(kwArgs.keys()).issubset(set(kwParamDefaults.keys())) and len(posArgs) == 0:
                        newDict = dict(kwParamDefaults)
                        newDict.update(kwArgs)
                        return cls(self.orig, **kwArgs)
            cls.__call__ = newCall
            return cls
        return subWrap

@initInstDesc.createDesc('e0', {'depth': 0})
@initInstDesc.createDesc('e')
class elementWise:
    def __init__(self, Iter, depth=None):
        self.type = type(Iter)
        self.elems = list(Iter)
        self.depth = depth

    def chooseCanElemWise(elem, prevDepth=None):
        try:
            type(elem)([])
            if prevDepth is None:
                return elem.e
            else:
                return elem.e(depth=prevDepth-1)
        except:
            return elem

    def tryFunc(self, func, *posArgs):
        try:
            if all([len(arg) == len(self.elems) for arg in posArgs]):
                returnList = [elementWise.process(func)(*([elementWise.chooseCanElemWise(elem, self.depth)] + [arg[i] for arg in posArgs])) for i, elem in enumerate(self.elems)]
            else:
                raise ValueError('Cannot match argument')
        except:
            returnList = [elementWise.process(func)(*([elementWise.chooseCanElemWise(elem, self.depth)] + list(posArgs))) for elem in self.elems]
        return self.type(returnList)

    reorderParams = lambda func, reversePermute : lambda *permutedArgs : func(*[permutedArgs[reversePermute[x]] for x in range(len(permutedArgs))])

    def convertDepth0Args(arg):
        if type(arg) is elementWise:
            if arg.depth == 0:
                return arg.type(arg.elems)
        return arg

    toOnlyPosArgs = lambda func, kwArgNames : lambda *posArgs : func(*posArgs[len(kwArgNames):], **{var: posArgs[i] for i, var in enumerate(sorted(kwArgNames))})
    
    def process(func):
        def newFunc(*posArgs, **kwArgs):
            if len(kwArgs) > 0:
                return elementWise.process(elementWise.toOnlyPosArgs(func, kwArgs.keys()))(*([kwArgs[key] for key in sorted(kwArgs.keys())] + list(posArgs)))
            else:
                if any([type(arg) is elementWise for arg in posArgs]):
                    ordered = True
                    for arg, nextArg in zip(posArgs[:-1], posArgs[1:]):
                        if type(arg) != elementWise and type(nextArg) is elementWise:
                            ordered = False
                            break
                        elif type(arg) is elementWise and type(nextArg) is elementWise:
                            if arg.depth == 0 and nextArg.depth != 0:
                                ordered = False
                                break
                    if ordered:
                        posargs = list(map(elementWise.convertDepth0Args, posArgs))
                        arg1 = posargs.pop(0)
                        if type(arg1) is elementWise:
                            return arg1.tryFunc(func, *posargs)
                        else:
                            return func(arg1, *posargs)
                    else:
                        beginList, endList, middleList, beginArgs, endArgs, depth0args = [[] for i in range(6)]
                        for i, arg in enumerate(posArgs):
                            if type(arg) is elementWise:
                                if arg.depth == 0:
                                    depth0args.append(arg)
                                    middleList.append(i)
                                else:
                                    beginArgs.append(arg)
                                    beginList.append(i)
                            else:
                                endArgs.append(arg)
                                endList.append(i)
                        permuteList, permutedArgs = beginList + middleList + endList, beginArgs + depth0args + endArgs
                        reversePermute = {y:x for x, y in enumerate(permuteList)}
                        return elementWise.process(elementWise.reorderParams(func, reversePermute))(*permutedArgs)
                else:
                    return func(*posArgs)
        return newFunc

    __getattr__ = lambda self, attr : lambda *posArgs : elementWise.process(lambda x, *otherPosArgs : eval('x.' + attr + '(*otherPosArgs)'))(self, *posArgs)

    for operatorName in SAFE_OVERLOADABLE_OPERATORS:
        try:
            exec('''def __''' + operatorName + '''__(self, *posArgs):
    method = self.__getattr__(''' + "'__" + operatorName +  "__'" + ''')
    return method(*posArgs)''')
        except Exception as err:
            print(operatorName)
            print(err)
            pass

