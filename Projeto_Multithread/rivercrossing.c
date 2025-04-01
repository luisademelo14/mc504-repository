#include <pthread.h>
#include <semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int hackers = 0;
int serfs = 0;
int isCaptain = 0;
sem_t mutex;
sem_t hackerQueue;
sem_t serfQueue;
sem_t barrier;
sem_t boat;
sem_t boatMutex;
sem_t captainMutex;       

int main(){

    mutex.wait();
    hackers += 1;
    if (hackers == 4){
        hackerQueue.signal(4);
        hackers = 0;
        isCaptain = 1;
    }
    else if (hackers == 2 && serfs >= 2){
        hackerQueue.signal(2);
        serfQueue.signal(2);
        serfs -= 2;
        hackers = 0;
        isCaptain = 1;
    }
    else {
        mutex.signal(); // captain keeps the mutex
    }

    hackerQueue.wait();

    board();
    barrier.wait();

    if isCaptain{
        rowBoat();
        mutex.signal(); // captain releases the mutex
    }

    return 0;
}

