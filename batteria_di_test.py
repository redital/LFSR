from LFSR import *
import matplotlib.pyplot as plt
import numpy


if __name__ == "__main__":
    #   Costanti
    plot = True
    bit_number = 16
    state = 1<<(bit_number-1) | 1
    n = 1<<22
    subprocess_n = 16

    n_test = 5
    
    #   Approccio sincrono
    f_under_test = batteria_di_test(sync_simulation,n_test)
    times_s = f_under_test(bit_number,n,state)

    #   Approccio multithread
    f_under_test = batteria_di_test(multiprocess_simulation,n_test)
    times_m = f_under_test(bit_number,n,state, subprocess_n)
    
    #   plot
    x,s = list(times_s.keys()), list(times_s.values())
    m = list(times_m.values())
    setUp = m[0] - s[0]
    scale = [s_i / x_i for s_i,x_i in zip(s,x)]
    scale = numpy.mean(scale)
    print(scale)
    scaled_x = [i*scale for i in x]
    expected = [setUp + (i) for i in scaled_x]
    fig = plt.figure()
    plt.plot(x,s,x,m)
    plt.plot(x,scaled_x, ".", x,expected, ".")
    plt.legend(['Synchronous', 'Multiprocess','Expected Synchronous', 'Expected Multiprocess'])
    plt.ylabel('Tempo di esecuzione')
    plt.xlabel('Numero di campioni generati')
    plt.show()