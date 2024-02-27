# LFSR
Implementazione di un generatore di numeri pseudocasuali tramite il meccanismo Linear Feedback Shifted Register

Oltre alla semplice impelentazione, il codice prevede anche un confronto a livello computazionale di diversi metodi per l'esecuzione di programmi di calcolo, si esplorano in particolare gli approcci 
- Sincrono
- Asinchrono
- Multiprocess
- Multithread

L'implementazione è piuttosto parametrica ma l'LFSR implementato è quello descritto dal polinomio $P = 1 + x + x^3 + x^5 + x^7$

Per sua natura un LFSR genera campioni provenienti da una uniforme, si è poi voluto sfruttare questi ultimi per generare campioni da una esponenziale e da una normale
