# In this file I will present you some example code on how to use the Multiprocessing for Kids
# package. I hope this makes it really easy for you to use it in your own projects

# Just uncomment the example function you want to see on the bottom. There is also a detailed
# description to every example. (inside the if __name__ == "__main__": statement on the bottom)

import multiprocessing_for_kids as mulki
import random
import time

''' Example 1: count 2 million '''
# split in 10 tasks, each counting to 200 thousand
# 3 static arguments
# no shared variables
# no return variable


def countTo(iter_val, goal, steps, _print):
    t0 = time.time()

    step_range = int(goal / steps)  # goal = 2 million, steps = 10 -> step_range = 200k

    _from = (iter_val - 1) * step_range     # e.g. step 1: 1-1 * 200k = 0
    _to = iter_val * step_range             # e.g. step 1: 1 * 200k = 200k

    ''' the actual counting: '''
    for i in range(_from, _to + 1):         # _to + 1 to get to 200k instead of 199.999
        if _print:
            print(i)

    # Print the current job and time it took to execute:
    print("Finished:", iter_val, " from ", _from, " to ", _to, "in",
          round(time.time() - t0, 1), "s")

def example1(_print = False, without_mp = False):
    # In this first example we count in 10 steps to 2 million. Each step is handled by a
    # different process. So our iterator counts from 1 to 10. We could also count in
    # 100 episodes to 2 million. Just change the iterator to range(1,101)
    print("Start...")
    t_start_mp = time.time()
    iterator = range(1, 5)     # 1,2,3,4,5,6,7,8,9,10
    goal = 2000000              # counting goal
    if not _print:              # if we don't print every number
        goal = goal * 1000      # we count to 2 billion instead of 2 million

    # With Multiprocessing:
    mulki.doMultiprocessingLoop(countTo, iterator, False, goal, len(iterator), _print)
    print("Finished counting with Multiprocessing in ", round(time.time()-t_start_mp, 1), "s")

    # Without Multiprocessing:
    if without_mp:
        t_start_normal = time.time()
        countTo(1, goal, 1, _print)
        print("Finished counting without Multiprocessing in ", round(time.time()-t_start_normal, 1), "s")



''' Example 2: edit and print shared Variables '''
# no static arguments
# 2 shared variables
# no return variable

def changeSharedVar(iter_val, var1, var2):
    # Important: Change the var.value property, not the var directly
    for i in range(1000):#random.randrange(100,10000)):
        var1.value += 1
    print("var1 = ", var1.value)
    var2.value += "o"
    print("Process Nr:", iter_val, " var2 =", var2.value)

def example2():
    # Now we want to use two shared variables. Therefore, we count randomly to get
    # different timeframes in each separate process. This way the variables are changed
    # and printed at different times from different processes.
    var1 = 0
    var2 = "Hello"
    mulki.addSharedVars(var1, var2)
    mulki.doMultiprocessingLoop(changeSharedVar, range(10))


''' Example 3: return as soon as a result was found '''
# let the processes all do the same searching task and the first one who finds a solution
# returns it.
# 2 static arguments
# 1 shared variable
# 1 return variable

def seach_the_number(_, the_number, search_range, attempt):
    # !!! First the iterator then the static vars then the shared vars !!!
    # The task is to find a given Number between 0 and 10.000
    guess = 0
    while guess != the_number:
        attempt.value += 1
        guess = random.randrange(search_range)
    return guess

def example3():
    t_start = time.time()   # measure time

    search_range = 10000    # modify this for longer searching times

    the_number = random.randrange(search_range) # the process that finds this Number wins
    print("Number to guess: ", the_number)

    mulki.addSharedVars(0) # attempts as shared var
    result = mulki.doMultiprocessingLoop(seach_the_number, range(100), True, the_number, search_range)

    print("Correct guess:", result[0], "after", mulki.getSharedVarsAsValues()[0], "attempts [time:", round(time.time() - t_start, 1), "s]")




if __name__ == "__main__":
    example1(False) # uncomment this to see example 1. Read notes below
    # For better understanding what the example is doing run example1(False).
    # As we can see it counts from 0 to 2 billon in 10 (printed) steps. Each step runs
    # in a separate process so we use 100% of CPU. If you don't see your CPU
    # fully occupied, just increase the goal value in example1()

    # As you run example1(False) you can see Steps "Finished: 2 ...", "Finished: 1.."
    # finishing at kind of the same time. The number of steps finishing at (nearly) the same
    # time is the amount of CPU's that are used. Each process counts a different range and each
    # process has been running on a different processor. After the first e.g. 4 ranges are
    # done counting through, the e.g. 4 CPU's are back available and start with the next
    # 4 ranges (steps) of counting. That's why 4 steps always finish in (nearly) the same time
    # (if you have 4 CPU's).

    # Sometimes we see processes not finishing in the Order they are started. That's the
    # prove that there are actually multiple processes running in parallel on different
    # CPU's. We can even see the counting of the processes and the current values if we run
    # example1(True) # (uncomment this) don't forget to comment example1() above
    # As we can see, the order is mixed up.

    # To Compare the time to "normal" counting on one CPU without multiprocessing, run:
    # example1(False, True)

    # If we don't want to split the counting task or we want to do the counting (or another
    # task) in order, we have to use shared variables as we can see in example2.



    # example2() # uncomment this and comment example1() above
    # As we can see, the output (print) of var1 is always in order (increasing over time) even
    # when the processes finished after different time frames (because counting to values
    # between 100 and 10k).
    # With this we have proven that all processes are manipulating the same shared variables
    # Sharing variables also works with strings (var2), floats, lists,
    # dicts, and queues (queues not recommended, see Multiprocessing_for_kids.py for more info)
    # You can add more types by manipulating the "__varToValue()" function in
    # Multiprocessing_for_kids.py



    # example3()
    # Here we are showing that the termination process with a return value (the result)
    # works fine. So, whenever you need to do a calculation that requires a lot of time and
    # resources but you don't know exactly when it's finished, you can set
    # terminateIfValReturned = True and return from your function whenever it's done.
    # This will trigger a callback, terminate all processes and return the return value.

    # trying to make the results reproducible (e.g. with random.seed(1)) is not completely
    # possible because the CPU's take different times for the calculations depending on their
    # other tasks.

    # Author: Sebastian Nichtern

    ''' Ideas for future examples: ''' # feel free to implement and pull request
    # 1. Return without termination after each process has finished (one run of the given
    #    function)
    # 2. Realworld practical usecase of multi processing (e.g. prime factorization, knn or
    #    some other expensive algorithm)
