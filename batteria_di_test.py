from LFSR import *
import matplotlib.pyplot as plt
import numpy
from multiprocessing.pool import Pool
import multiprocessing.pool


if __name__ == "__main__":
    print("CPU cores number:",multiprocessing.cpu_count())

    #   Costanti
    plot = True
    bit_number = 16
    state = 1<<(bit_number-1) | 1
    n = 1<<22
    subprocess_n = 16

    n_test = 150

    #   Approccio multiprocess
    f_under_test = batteria_di_test(multiprocess_simulation,n_test)
    t1 = f_under_test(bit_number,n,state, 1)
    t2 = f_under_test(bit_number,n,state, 2)
    t4 = f_under_test(bit_number,n,state, 4)
    t8 = f_under_test(bit_number,n,state, 8)
    t16 = f_under_test(bit_number,n,state, 16)
    
    x,y1 = list(t1.keys()), list(t1.values())
    y2 = list(t2.values())
    y4 = list(t4.values())
    y8 = list(t8.values())
    y16 = list(t16.values())
    scale = [y1_i / x_i for y1_i,x_i in zip(y1,x)]
    scale = numpy.mean(scale)

    scaled_x = [i/80000 for i in x]

    e1 = [(y1[i] - y1[i+1])/(scaled_x[-1] - scaled_x[0]) for i in range(len(y1)-1)]
    e1 = -numpy.mean(e1)
    e2 = [(y2[i] - y2[i+1])/(scaled_x[-1] - scaled_x[0]) for i in range(len(y2)-1)]
    e2 = -numpy.mean(e2)
    e4 = [(y4[i] - y4[i+1])/(scaled_x[-1] - scaled_x[0]) for i in range(len(y4)-1)]
    e4 = -numpy.mean(e4)
    e8 = [(y8[i] - y8[i+1])/(scaled_x[-1] - scaled_x[0]) for i in range(len(y8)-1)]
    e8 = -numpy.mean(e8)
    e16 = [(y16[i] - y16[i+1])/(scaled_x[-1] - scaled_x[0]) for i in range(len(y16)-1)]
    e16 = -numpy.mean(e16)
    print(e1,e2,e4,e8,e16)

    l=[e1,e2,e4,e8,e16]
    a = []
    for i,p in zip(l,[1,2,4,8,16]):
        a.append((i/l[0])*p)
        print(a[-1])
    
    x_a = list(range(5))
    ea=(a[-1]-a[0])/4
    print(ea)

    plt.figure()
    plt.plot(x_a, a, x_a, [i*ea + a[0] for i in x_a])
    plt.figure()
    x_a = [2**x for x in x_a]
    ea=(a[-1]-a[0])/16
    plt.plot(x_a, a, x_a, [i*ea + a[0] for i in x_a])

    plt.figure()
    plt.plot(x,y1,x,y2,x,y4,x,y8,x,y16,)
    plt.legend(['1','2','4','8','16'])
    plt.ylabel('Tempo di esecuzione')
    plt.xlabel('Numero di campioni generati')
    #plt.show()





















    
    n_test = 100
    
    #   Approccio sincrono
    f_under_test = batteria_di_test(sync_simulation,n_test)
    times_s = f_under_test(bit_number,n,state)

    #   Approccio multiprocess
    f_under_test = batteria_di_test(multiprocess_simulation,n_test)
    times_m = f_under_test(bit_number,n,state, subprocess_n)
    
    #   plot
    x,s = list(times_s.keys()), list(times_s.values())
    m = list(times_m.values())
    scale = [s_i / x_i for s_i,x_i in zip(s,x)]
    scale = numpy.mean(scale)
    print(m[0],s[0],m[0]-s[0])
    scaled_x = [i*scale for i in x]
    expected = [m[0] + (i)*(ea + (a[0]/subprocess_n)) for i in scaled_x]
    expected_fixed = [m[0] + (i)*(0.95 + (a[0]/subprocess_n)) for i in scaled_x]
    #0.95 per pc fisso
    #1.55 per pc lavoro
    plt.figure()
    plt.plot(x,s,x,m)
    plt.plot(x,scaled_x, ".", x,expected, ".")
    plt.legend(['Synchronous', 'Multiprocess','Expected Synchronous', 'Expected Multiprocess'])
    plt.ylabel('Tempo di esecuzione')
    plt.xlabel('Numero di campioni generati')


    plt.figure()
    plt.plot(x,s,x,m)
    plt.plot(x,scaled_x, ".")
    plt.plot(x,expected_fixed, ".")
    plt.legend(['Synchronous', 'Multiprocess','Expected Synchronous', 'Expected Multiprocess'])
    plt.ylabel('Tempo di esecuzione')
    plt.xlabel('Numero di campioni generati')


    plt.show()