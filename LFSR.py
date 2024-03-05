import time
import asyncio
import matplotlib.pyplot as plt
import numpy
from multiprocessing.pool import Pool
import concurrent.futures

def performance_timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        data = func(*args, **kwargs)
        end = time.perf_counter()
        message_format = "\nExecution time {}: {:.4f} s"
        print(message_format.format(func.__name__, end-start))
        return data
    return wrapper

def batteria_di_test(func, n_test, initial_n = 1_000_000, delta_n = 80_000):
    def wrapper(*args, **kwargs):
        total_n = int(n_test*initial_n + delta_n*((n_test*(n_test+1))/2))
        processed_n = 0
        ns = [initial_n + delta_n*i for i in range (n_test)]
        times = {}
        l=20
        for n in ns:
            perc = processed_n/total_n
            p = int(perc)*l
            print("[" + "="*p + " "*(l-p) +"]", "{:.2f}%".format(perc*100),sep="\t", end="\r")

            start = time.perf_counter()
            args = list(args)
            args[1] = n
            func(*args, **kwargs)
            end = time.perf_counter()
            times[n] = end-start
        perc = processed_n/total_n
        p = int(perc)*l
        print("[" + "="*p + " "*(l-p) +"]", "{:.2f}%".format(perc*100),sep="\t")
        return times
    return wrapper

#@performance_timer
def plot_hist(data, bins = 15, title="", show = False, save = False):
    _ , grafico = plt.subplots()
    grafico.hist(x = data, 
                bins = bins,
                ec = "grey",
                fc = "orange" )
    
    if title: plt.title(title)

    if show: plt.show()

    if save: plt.savefig()

def simulate(bit_number, n, initial_state, bar = False, l = 20):
    gen = simulate_gen(bit_number, initial_state)
    data = []
    for i in range(n):
        if bar:
            perc = i/((n)-1)
            p = int((i/((n)-1))*20)
            print("[" + "="*p + " "*(l-p) +"]", "{:.2f}%".format(perc*100), end="\r")
        data.append(next(gen))
    return data

def simulate_gen(bit_number, initial_state):
    state = initial_state
    while(True):
        #print("{:08b}".format(state))
        #print(state & 1)
        newbit = (((((state ^ state>>1) ^ state>>5) ^ state>>7) ^ state>>3)) & 1
        state = state>>1 | newbit<<(bit_number-1)
        yield state
    
def sync_simulation(bit_number, n, initial_state, bar = False, l = 20, norm = False):
    data = simulate(bit_number, n, initial_state, bar, l)
    if norm: data = [(i/(1<<bit_number)) for i in data]
    return data

async def simulate_corutine(bit_number, n, initial_state):
    return simulate(bit_number, n, initial_state)

async def async_simulation_process(bit_number, n, states):
    funcs = [simulate_corutine(bit_number,int(n/len(states)),state) for state in states]
    data = await asyncio.gather(*funcs)
    return data

def async_simulation(bit_number, n, state, subprocess_n, norm = False):
    states = simulate(bit_number,subprocess_n,state)
    data = asyncio.run(async_simulation_process(bit_number, n, states))
    data = [i for riga in data for i in riga]
    if norm: data = [(i/(1<<bit_number)) for i in data]
    return data

def multiprocess_simulation(bit_number, n, state, subprocess_n = 16, norm = False):
    states = simulate(bit_number,subprocess_n,state)
    with Pool() as pool:
        data = pool.starmap(simulate,[(bit_number,int(n/len(states)),state) for state in states])
    data = [i for riga in data for i in riga]
    if norm: data = [(i/(1<<bit_number)) for i in data]
    return data

def multithread_simulation(bit_number, n, state, subprocess_n = 16, norm = False):
    states = simulate(bit_number,subprocess_n,state)
    with concurrent.futures.ThreadPoolExecutor(max_workers=subprocess_n) as executor:
        data = executor.map(simulate,[bit_number for _ in states],[int(n/len(states)) for _ in states],states)
    data = [i for riga in data for i in riga]
    if norm: data = [(i/(1<<bit_number)) for i in data]
    return data

def simulate_norm_exp(bit_number,n,initial_state,v=1,m=0, bar= False, l = 20):
    gen = simulate_gen(bit_number, initial_state)
    exponential = []
    normal = []
    
    while len(exponential)<n or len(normal)<n:
        if bar:
            perc = len(normal)/((n)-1)
            p = int((len(normal)/((n)-1))*20)
            print("[" + "="*p + " "*(l-p) +"]", "{:.2f}%".format(perc*100),sep="\t", end="\r")
        u_1 = next(gen)/(1<<bit_number)
        u_2 = next(gen)/(1<<bit_number)
        y_1 = -numpy.log(u_1)
        y_2 = -numpy.log(u_2)
        if y_2 > ((1 - y_1)**2)/2:
            exponential.append(y_1)
            exponential.append(y_2)

            state = next(gen)

            if state/(1<<bit_number) < 1/2:
                normal.append(y_1)
            else:
                normal.append(-y_1)
    if bar: print()
    return normal, exponential

@performance_timer
def multiprocess_norm_exp_simulation(bit_number, n, state, subprocess_n, norm = False,v=1,m=0, bar= False, l = 20):
    states = simulate(bit_number,subprocess_n,state)
    with Pool() as pool:
        data =  pool.starmap(simulate_norm_exp,[(bit_number,int(n/len(states)),state,v,m, bar, l) for state in states])
        normal, exponential =  [i for t in data for i in t[0]],[i for t in data for i in t[1]]
    if norm: data = [(i/(1<<bit_number)) for i in data]
    return normal, exponential

#   C'è un problema riguardante i processi con sottoprocessi, ogni sottoprocesso allo stato attuale è uguale al precedente ma solo shiftato in avanti di 1
if __name__ == "__main__":
    #   Costanti
    plot = False
    bit_number = 16
    state = 1<<(bit_number-1) | 1
    n = 1<<22
    subprocess_n = 16

    print("Generating data, I want {} samples".format(n))

    #   Approccio sincrono
    f_under_test = performance_timer(sync_simulation)
    data = f_under_test(bit_number,n,state)
    if plot : plot_hist(data,title="Synchronous")

    #   Approccio asincrono
    f_under_test = performance_timer(async_simulation)
    data = f_under_test(bit_number,n,state, subprocess_n)
    if plot : plot_hist(data,title="Asynchronous")

    #   Approccio multiprocess
    f_under_test = performance_timer(multiprocess_simulation)
    data = f_under_test(bit_number,n,state, subprocess_n)
    if plot : plot_hist(data,title="Multiprocessing")

    #   Approccio multithread
    f_under_test = performance_timer(multithread_simulation)
    data = f_under_test(bit_number,n,state, subprocess_n)
    if plot : plot_hist(data,title="Multithreading")
    
    #   Sfrutto i dati simulati (che vengono da una normale) per simulare una distribuzione normale ed una esponenziale
    normal,exponential = multiprocess_norm_exp_simulation(bit_number,n,state,subprocess_n)
    if plot : plot_hist(normal)
    if plot : plot_hist(exponential)

    if plot : plt.show()
