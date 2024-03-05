from LFSR import *
import matplotlib.pyplot as plt
import numpy
import multiprocessing.pool


if __name__ == "__main__":
    print("CPU cores number:",multiprocessing.cpu_count())
    
    print("Costruzione del modello")

    #   Costanti
    plot = True
    bit_number = 16
    state = 1<<(bit_number-1) | 1
    n = 1<<22
    subprocess_n = 8

    n_test = 30

    keys = [2**i for i in range(4)]
    t = {}

    #   Fase 1: ESECUZIONE DEI TEST CON DIVERSI NUMERI DI PROCESSI AL FINE DI SCRIVERE IL MODELLO
    
    #   Faccio una simulazione in modalità sincrona solo per calcolare il fattore di scaling (da provare usando n_test piccolo) 
    f_under_test = batteria_di_test(sync_simulation,10)
    sync = f_under_test(bit_number,n,state)

    #   Test al variare del numero di processi
    f_under_test = batteria_di_test(multiprocess_simulation,n_test)
    for k in keys:
        t[k] = f_under_test(bit_number,n,state, k)
    
    #   Recupero x e y di ogni test per i plot 
    x = list(t[keys[0]].keys())
    y = {k:list(t[k].values()) for k in keys} 
    sync = list(sync.values())
    
    #   Calcolo la costante di riscalamento
    scale = [yi / x_i for yi,x_i in zip(sync,x)]
    scale = numpy.mean(scale)

    #   Stima dei coefficienti angolari delle rette interpolanti i risultati dati dai test
    e={}
    for k in keys:
        e[k] = [(y[k][i+1] - y[k][i])/(x[i+1] - x[i]) for i in range(len(y[k])-1)]
        e[k] = numpy.mean(e[k])

    #   Primo plot in cui mostro la natura inversamente proporzionale del rapporto tra il numero di processi e il coefficiente angolare
    plt.figure()
    plt.title("e")
    plt.plot(keys, list(e.values()))

    #   Calcolo a da cui dipende il coefficiente angolare e la sua versione alernativa alpha
    a = []
    alpha = []
    for p,e_p in e.items():
        alpha.append((e_p/e[keys[0]])*p)
        a.append((e_p/scale)*p) 
    
    #   Stima del coefficiente angolare della retta interpolante i valori di a trovati
    x_a = keys
    ea=(a[-1]-a[0])/(x_a[-1]-x_a[0])
    ealpha=(alpha[-1]-alpha[0])/(x_a[-1]-x_a[0])
    #   Stima del termine noto della retta interpolante i valori di a trovati
    initial_a = [a[i]-(x_a[i]*ea) for i in range(len(x_a))]
    initial_a = numpy.mean(initial_a)
    initial_alpha = [alpha[i]-(x_a[i]*ealpha) for i in range(len(x_a))]
    initial_alpha = numpy.mean(initial_alpha)
    #   Plot di a e alpha calcolati vs relativa retta interpolante
    plt.figure()
    plt.title("alpha")
    plt.plot(x_a, alpha, x_a, [i*ealpha + initial_alpha for i in x_a])
    plt.legend(["actual", "expected"])
    plt.figure()
    plt.title("a")
    plt.plot(x_a, a, x_a, [i*ea + initial_a for i in x_a])
    plt.legend(["actual", "expected"])
    plt.figure()
    #   Plot di e vs relativa iperbole interpolante calcolata sia con a che con alpha
    plt.title("e")
    plt.plot(x_a, e.values(), x_a, [(i*ea + initial_a)*(scale/i) for i in x_a],x_a, [(i*ealpha + initial_alpha)*a[0]*(scale/i) for i in x_a])
    plt.legend(["actual", "expected (a computed)", "expected (alpha computed)"])

    #   Plot delle rilevazioni
    plt.figure()
    for k in keys:
        plt.plot(x,y[k])
    plt.legend([str(k) for k in keys])
    plt.ylabel('Tempo di esecuzione')
    plt.xlabel('Numero di campioni generati')
    plt.show()





    
    #   Fase 2: ESECUZIONE DEI TEST AL FINE DI VALIDARE IL MODELLO
    print("Validazione del modello")

    n_test = 80
    
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
    scaled_x = [i*scale for i in x]
    initial_m = [m[i]-(scaled_x[i])*(ea + (initial_a/subprocess_n)) for i in range(len(scaled_x))]
    initial_m = numpy.mean(initial_m)
    expected = [initial_m + (i)*(ea + (initial_a/subprocess_n)) for i in scaled_x]
    expected_alpha = [initial_m + i*a[0]*(ealpha + (initial_alpha/subprocess_n)) for i in scaled_x]

    plt.figure()
    plt.plot(x,s,x,m)
    plt.plot(x,scaled_x, ".", x,expected, ".")
    plt.legend(['Synchronous', 'Multiprocess','Expected Synchronous', 'Expected Multiprocess'])
    plt.ylabel('Tempo di esecuzione')
    plt.xlabel('Numero di campioni generati')


    plt.figure()
    plt.plot(x,s,x,m)
    plt.plot(x,scaled_x, ".")
    plt.plot(x,expected_alpha, ".")
    plt.legend(['Synchronous', 'Multiprocess','Expected Synchronous', 'Expected Multiprocess'])
    plt.ylabel('Tempo di esecuzione')
    plt.xlabel('Numero di campioni generati')


    plt.show()