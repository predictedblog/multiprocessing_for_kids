# In this file I will present you some example code on how to use the Multiprocessing for Kids
# package. I hope this makes it really easy for you to use it in your own projects

# Just uncomment the example function you want to see on the bottom. There is also a detailed
# description to every example. (inside the if __name__ == "__main__": statement on the bottom)

import multiprocessing_for_kids as mulki
import random
import time
from ortools.algorithms import pywrapknapsack_solver
from multiprocessing import cpu_count, Lock


''' Example 1: count 2 million '''
# split in 10 tasks, each counting to 200 thousand or 200 million
# 3 constant arguments
# no shared variables
# no return value

def countTo(iter_val, GOAL, STEPS, PRINT):
    t0 = time.time()

    STEP_RANGE = int(GOAL / STEPS)  # goal = 2 million, steps = 10 -> step_range = 200k

    FROM = (iter_val - 1) * STEP_RANGE     # e.g. step 1: 1-1 * 200k = 0
    TO = iter_val * STEP_RANGE             # e.g. step 1: 1 * 200k = 200k

    ''' the actual counting: '''
    for i in range(FROM, TO + 1):         # TO + 1 to get to 200k instead of 199.999
        if PRINT:
            print(i)

    # Print the current job and time it took to execute:
    print("Finished:", iter_val, " from ", FROM, " to ", TO, "in",
          round(time.time() - t0, 1), "s")

def example1(PRINT = False, WITHOUT_MP = False):
    # In this first example we count in 10 steps to 2 million. Each step is handled by a
    # different process. So our iterator counts from 1 to 10. We could also count in
    # 100 episodes to 2 million. Just change the iterator to range(1,101)
    print("Start...")
    t_start_mp = time.time()
    iterator = range(1, 11)     # 1,2,3,4,5,6,7,8,9,10
    GOAL = 2000000              # counting goal
    if not PRINT:               # if we don't print every number
        GOAL = GOAL * 1000      # we count to 2 billion instead of 2 million

    # With Multiprocessing:
    mulki.doMultiprocessingLoop(countTo, iterator, False, GOAL, len(iterator), PRINT)
    print("Finished counting with Multiprocessing in ", round(time.time()-t_start_mp, 1), "s")

    # Without Multiprocessing:
    if WITHOUT_MP:
        t_start_normal = time.time()
        countTo(1, GOAL, 1, PRINT)
        print("Finished counting without Multiprocessing in ", round(time.time()-t_start_normal, 1), "s")




''' Example 2: Search the Number '''
# let the processes all do the same searching task and write it into a shared variable.
# 2 constant arguments
# 1 shared variable
# no return value

def seach_the_number(_, THE_NUMBER, SEARCH_RANGE, result):
    # The task is to find a given Number between 0 and 100.000
    guess = 0
    while guess != THE_NUMBER:
        guess = random.randrange(1, SEARCH_RANGE)
        if result.value != 0:
            break
    else: # only if the loop breaks by its termination condition
        result.value = guess

def example2():
    t0 = time.time()         # measure time

    SEARCH_RANGE = 100000    # modify this for longer searching times
    THE_NUMBER = random.randrange(1, SEARCH_RANGE)  # search result
    print("Number to guess: ", THE_NUMBER)

    print("Start guessing...")
    result = 0
    mulki.addSharedVars(result) # result as shared var
    mulki.doMultiprocessingLoop(seach_the_number, range(cpu_count()), False, THE_NUMBER, SEARCH_RANGE)

    print("Correct guess:", mulki.getSharedVarsAsValues()[0], "in ", round(time.time() - t0, 2), "s")



''' Example 3: Search the Number with termination '''
# let the processes all do the same searching task and write it into a shared variable.
# 2 constant arguments
# 1 shared variable
# no return value

def seach_the_number_ret(_, THE_NUMBER, SEARCH_RANGE): # attempt
    # First comes the iterator then the static vars then the shared vars !!!
    # The task is to find a given Number between 1 and SEARCH_RANGE
    guess = 0
    # current_attempts = 0

    while guess != THE_NUMBER:
        guess = random.randrange(SEARCH_RANGE)

        # attempt.value += 1
        # attempts counting (looks complex but is fast, but not 100% accurat.): # USE LOCK!
        #current_attempts += 1
        #if current_attempts > 20: # final attempt value will be max 4*20 guesses of the real number of attempts.
        #    attempt.value += current_attempts # save in shared var (USE LOCK)
        #    current_attempts = 0 # reset for next 20 attempts

    return guess

def example3():
    t0 = time.time()         # measure time

    SEARCH_RANGE = 100000    # modify this for longer searching times
    THE_NUMBER = random.randrange(SEARCH_RANGE) # search result
    print("Number to guess: ", THE_NUMBER)

    print("Start guessing...")
    result = mulki.doMultiprocessingLoop(seach_the_number_ret, range(100), True, THE_NUMBER, SEARCH_RANGE)

    print("Correct guess:", result[0], "in ", round(time.time() - t0, 2), "s")

    # print("Correct guess:", result[0], "after", mulki.getSharedVarsAsValues()[0], "attempts [time:", round(time.time() - t0, 1), "s]")




''' Example 4: count a shared variable '''
# This example shows the limits of shared variables. It should demonstrate what can go wrong
# and how to prevent this from happening.
# no constant arguments
# 1 shared variable
# no return value

lock = Lock()
def countTo_shared(_, PROCESS_GOAL, PRINT, counter):
    for _ in range(PROCESS_GOAL):
        lock.acquire()
        counter.value += 1
        lock.release()
        if PRINT:
            print(counter.value)

def example4(PRINT = True):
    print("Start...")
    t0 = time.time()
    GOAL = 100000          # counting goal = 100.000
    PROCESS_GOAL = int(GOAL / cpu_count())
    mulki.addSharedVars(0) # the counter variable
    mulki.doMultiprocessingLoop(countTo_shared, range(cpu_count()), False, PROCESS_GOAL, PRINT)
    print("Finished counting with Multiprocessing in ", round(time.time()-t0, 1), "s")



''' Example 5: search for optimal knapsack solution '''
# For explanation see my blog post at: https://predicted.blog/multiprocessing-knapsack-problem
# 3 constant arguments
# 2 shared variable
# no return variable

def knapsack_search(_, VOLUMES, PRICES, KNAPSACK_VOLUME, solution, solution_price):
    # Parameters: First the iterator then the static vars and then the shared vars !
    # Note to Shared variables: Change the .value property, not the variable directly.
    OBJECTS = len(VOLUMES)  # amount of objects
    t0 = time.time()
    while (time.time() - t0) < 60: # search for 20 seconds

        # Create a random filling of the knapsack:
        pick_positions = random.sample(list(range(OBJECTS)), OBJECTS)
        current_volumes = [VOLUMES[i] for i in pick_positions]

        # it's to full! Remove elements until the volume fits:
        for i in range(1, OBJECTS):
            current_volumes = current_volumes[:-1]
            if sum(current_volumes) <= KNAPSACK_VOLUME:
                pick_positions = pick_positions[:-i]
                break

        # calculate total price and check if it beats the current best
        total_price = sum([PRICES[i] for i in pick_positions])
        if total_price > solution_price.value:
            solution_price.value = total_price
            solution.value = pick_positions

        # Debugging:
        if round(time.time() - t0,0) in list(range(0,60,5)): # debugging
            print(round(time.time() - t0,0),"s, current best:",solution_price.value)


def example5():
    # We create our knapsack items and start the multiprocessing loop that uses the
    # knapsack_search() function above.
    OBJECTS = 20 # amount of items

    random.seed(42) # make volumes reproducible
    VOLUMES = [random.randint(20, 100) for _ in range(OBJECTS)] # random volumes for 100 Objects
    random.seed(42) # make prices reproducible
    PRICES  = [random.randint(10, 800) for _ in range(OBJECTS)] # random prices for 100 Objects

    KNAPSACK_VOLUME = int(sum(VOLUMES) / 4) # volume that fits in the knapsack (1/4 of all objects)

    solution = [0]
    solution_price = 0
    mulki.addSharedVars(solution, solution_price) # add shared vars to mulki

    mulki.doMultiprocessingLoop(knapsack_search, range(cpu_count()), False, VOLUMES, PRICES, KNAPSACK_VOLUME)

    print("random guessing solution: ", mulki.getSharedVarsAsValues()[1]) # in [0] are the actual items
    # print("sum volumes:", sum([VOLUMES[i] for i in mulki.getSharedVarsAsValues()[0]]), "max:", KNAPSACK_VOLUME)

    # Google Solver:
    t0 = time.time()
    solver = pywrapknapsack_solver.KnapsackSolver(
        pywrapknapsack_solver.KnapsackSolver.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, 'test')
    solver.Init(PRICES, [VOLUMES], [KNAPSACK_VOLUME])
    computed_value = solver.Solve()
    print("\nGoogle OR Optimal Solution (max):", computed_value)
    # packed_items = [x for x in range(len(PRICES))
    #                 if solver.BestSolutionContains(x)]
    # packed_prices = [PRICES[i] for i in packed_items]
    # print("Packed items: ", packed_items)
    print("found in", round(time.time()-t0,5),"s")






if __name__ == "__main__":
    # Uncomment the example you want to run and comment the other ones.
    example1(False) # https://predicted.blog/multiprocessing-for-kids/
    # example2()    # https://predicted.blog/multiprocessing-for-kids-shared-variables/
    # example3()    #                    - " -
    # example4()    #                    - " -
    # example5()    # https://predicted.blog/multiprocessing-knapsack-problem

    # Author: Sebastian Nichtern


    ''' Ideas for future examples: ''' # feel free to implement and pull request
    # 1. Return without termination after each process has finished.
    #    Mulki returns the value after all processes have finished.
    # 2. ...
