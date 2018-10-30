# With this package multiprocessing is made easy. Just call the doMultiprocessingLoop()
# function and give it the function you want to execute in multiple processes, as well
# as an iterator and static arguments. You can add shared variables that can be seen and
# changed within all processes.
# It's also possible to return a value (of nearly any type) from the function that is
# looped over (loopFunction_). Therefore set terminateIfValReturned = True. This terminates
# all processes when a result is returned by your function (e.g. a solution you where searching
# for was found).
# If terminateIfValReturned = False and values are returned by the loopFunction_, the
# doMultiprocessingLoop() will return a list with the return values in each step after your
# loop has finished. (However this is not tested enough to be 100% secure. Please make some
# test on your own.)

# We now can get python to use 100% of the CPU's instead of just one.

# You can copy this file direktly into your project or into the site-packages folder of your
# python distribution to make it accessible in all of your Python projects.
from multiprocessing import Pool,Manager,managers,cpu_count,TimeoutError # ,Lock
from ctypes import c_wchar_p
import warnings

NUM_OF_PARALLEL_PROCESSES = cpu_count() # for max performance use cpu_count().

m = Manager()
# sharedVariables = m.list() # this causes dificuilties when adding queue Vars. And i found that a normal List also dose the job:
sharedVariables = [] # change them with variable.value = ...

def __varToValue(var):
    # Multiprocessing works with Values instead of normal Variables
    # This Function does the transformation for you
    if isinstance(var, (int, list)):
        return m.Value('i',var)
    elif isinstance(var, float):
        return m.Value('d',var)
    elif isinstance(var, str):
        return m.Value(c_wchar_p, var)
    elif isinstance(var, dict):
        return m.dict(var)
    elif type(var).__name__ == 'Queue':
        q = m.Queue(var.maxsize+1)
        # To get the queue as a list use the managerQueueToList() Function in this Module
        # !But try _not_ to use this! Use a Dict if you need it as a List anywhere! See the managerQueueToList() for more Info
        warnings.warn("Using Queue is not recomended! Try to use a dict or list instead.")
        if not var.empty():
            for element in iter(var.get, None): # transfer all queue elements to the manager queue
                q.put(element)
        return q
    # set() is not available. Use Dict instead. [https://stackoverflow.com/a/37714759/7699319]
    else:
        print("This Type: \""+str(type(var).__name__)+"\" cannot be shared. Use list, int, float, string, dict or queue")

def addSharedVars(*args):
    global sharedVariables
    for arg in args:
        sharedVariables.append(__varToValue(arg))

def setSharedVars(pos, val):
    global sharedVariables
    if type(sharedVariables[pos]).__name__ == 'ValueProxy':
        sharedVariables[pos].value = val
    elif type(sharedVariables[pos]).__name__ == 'DictProxy':
        sharedVariables[pos].value = val
    elif pos>=len(sharedVariables):
        print("can't set this shared Variable because the position"+ str(pos) +" dose not exist (index out of bounds). Function: setSharedVars in multiprocessing_for_kids")
    else:
        print("This is not a Value or Dict. The given type is not jet defined in the setSharedVars function")

def removeAllSharedVars():
    global sharedVariables
    sharedVariables = []

def resetSharedVars():
    global sharedVariables
    for i,var in enumerate(sharedVariables):
        if type(var).__name__ == 'ValueProxy':
            if type(var.value).__name__ == 'int':
                sharedVariables[i].value = 0
            if type(var.value).__name__ == 'list':
                sharedVariables[i].value = []
            if type(var.value).__name__ == 'float':
                sharedVariables[i].value = 0.0
            if type(var.value).__name__ == 'str':
                sharedVariables[i].value = ""
        elif type(var).__name__ == 'DictProxy':
            sharedVariables[i].clear()
        # set() is not available. Use Dict instead. [https://stackoverflow.com/a/37714759/7699319]
        else:
            print("This Type: \"" + str(type(var).__name__) + "\" is not supported by the resetSharedVars() function!")

def getSharedVars():
    return [var for var in sharedVariables]

def getSharedVarsAsValues():
    retVals = []
    for val in sharedVariables:
        if type(val) == managers.ValueProxy:
            retVals.append(val.value)
        elif type(val) == managers.DictProxy:
            retVals.append(dict(val.items()))
        else:
            retVals.append(val)
    return retVals

def managerQueueToList(queue, warning=True):
    # Returns the shared queue as a list.
    # this is _not_ a pretty good (+ slow) solution! Try to use Dict instead and check for its size
    # it can also happen that another process is writing something new into the Queue while
    # its refilled or emptied
    if warning:
        warnings.warn("This is a relatively slow method to convert the given Queue to a list. Please try to work with dicts if possible to avoid this.")
    queue_as_list = []
    while not queue.empty():
        queue_as_list.append(queue.get())
    for val in queue_as_list:
        if not queue.full():
            queue.put(val)
    return queue_as_list


terminated = False
def doMultiprocessingLoop(loopFunction_, loopIterator, terminateIfValReturned=False, *args):
    # loopFunction_: The Function that will be executed in a loop and in different processes. !Musst be a global Function! Functions in Functions don't work!
    # loopIterator: A List of elements passed to each function/process
    # *args: different Arguments that need to be passed to the Function and don't need to be shared (same in every loop iteration and process)

    #if len(loopIterator) > 600:
    #    warnings.warn("Error, loop iterator can only handle a limited amount of entries. "
    #                  "You probably missunderstood the way multiprocessing works."
    #                  "Only situations where the loopFunction_ takes a lot of computational power"
    #                  "and are executed in a limeted fassion are feasible for Multiprocessing.")
    #    return "Error, loop iterator can't have more than 600 entries"

    # Check if terminateIfValReturned is boolean or forgotten:
    if not isinstance(terminateIfValReturned, bool):
        raise ValueError("The third argument in doMultiprocessingLoop must be boolean. It represents if the processing should be terminated as soon as a value is returned by your function. Default value is False.")

    # Using Lock: https://www.geeksforgeeks.org/synchronization-pooling-processes-python/
    p = Pool(NUM_OF_PARALLEL_PROCESSES)  # my Macbook e.g. has 4 CPU's  # Pool() must be defined in the function where it's used!!
    def __callback(e):
        if terminateIfValReturned:
            global terminated
            if e == e: # check if e != None
                print("Terminating Multiprocessing...")
                terminated = True
                p.terminate()

    res = [None] * len(loopIterator) # Return Values. Is not actually needed if you use shared Vars..
    for i, iterVal in enumerate(loopIterator):
        res[i] = p.apply_async(loopFunction_, (iterVal, *args, *sharedVariables), callback=__callback)
    p.close()
    p.join()

    # FOR DEBUGGING: (This way you can check if specific processes have finished)
    # finished = [False] * len(loopIterator)
    # while True:
    #     sleep(0.0001)
    #     ready = [r.ready() for r in res]
    #     for i, rdy in enumerate(ready):
    #         if (rdy and not finished[i]):
    #             if PRINT_PROCESSES:
    #                 print("Process " + str(i) + " is done.")
    #             finished[i] = True
    #     if (sum(ready) == len(loopIterator)):
    #         break

    ''' Wait for Results ''' # if p.join() fails, wait here (happend, trust me)
    while True: # Checks if every Process is done.
        # sleep(0.0001) # maybe?
        if (sum([r.ready() for r in res]) == len(loopIterator)) or terminated:
            break

    ''' Return '''
    results = []
    for re in res: # all runs
        try:
            try:
                r = re.get(timeout=1)
            except TimeoutError: # A res Variable has nothing in it
                if terminated:
                    continue
                warnings.warn("Multiprocessing_for_kids TimeoutError. One of the return Values is not here jet for some reason. It will be skipped. This should never happen.")
                continue
            if r == r: # not None
                if isinstance(r, (int, float, str)):
                    results.append(r)
                elif type(r).__module__ == 'numpy':
                    results.append(r)
                elif len(r) < 2: # only one return Variable
                    if type(r).__name__ == 'ValueProxy':
                        results.append(r.value)
                    elif type(r).__name__ == 'DictProxy':
                        results.append(dict(r.items()))
                    else:
                        results.append(r)
                else:
                    for val in r:  # All return Variables
                        if type(val).__name__ == 'ValueProxy':
                            results.append(r.value)
                        elif type(val).__name__ == 'DictProxy':
                            results.append(dict(val.items()))
                        else:
                            results.append(val)
        except IndexError:
            if terminated:
                continue
            warnings.warn("Multiprocessing_me IndexError. One of the return Values will not be returned!") # I dont know why and I dont know a solution for this
        if terminated and results: # results not empty
            break # if terminated, ther will only be one result (the one from the callback)

    # print("MP return", results)
    return results


''' Examples on how to use this Module: '''
# Please see multiprocessing_for_kids_examples.py
# Or my blog posts here: predicted.blog/multiprocessing-for-kids
# and here: https://predicted.blog/multiprocessing-for-kids-shared-variables