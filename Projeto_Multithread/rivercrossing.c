#include <pthread.h>
#include <semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int hackers = 0;
int serfs = 0;
sem_t sem;
sem_t hackerQueue;
sem_t serfQueue;
pthread_barrier_t barrier_mutex;

void board(int id){
    // Simulate boarding process
    printf("%d Boarding...\n", id);
}

void rowBoat(int id){
    // Simulate rowing process
    printf("Rowing boat with Captain %d\n", id);
}

void* serf(void* arg){
    int id = (int) arg;  // Cast to int
    int isCaptain = 0;
    sem_wait(&sem);
    printf("Serf %d is waiting on queue\n", id);
    serfs += 1;
    if (serfs == 4){
        printf("ALL SERFS\n");
        // hackerQueue.signal(4);
        for (int i = 0; i < 4; i++){
            sem_post(&serfQueue);
        }
        serfs = 0;
        printf("Serf %d is captain\n", id);
        isCaptain = 1;
    }
    else if (hackers == 2 && serfs >= 2){
        printf("SERF: METADE CADA!!\n");
        sem_post(&hackerQueue);
        sem_post(&hackerQueue);
        sem_post(&serfQueue);
        sem_post(&serfQueue);
        // hackerQueue.signal(2);
        // serfQueue.signal(2);
        hackers -= 2;
        serfs = 0;
        isCaptain = 1;
    }
    else {
        sem_post(&sem); // captain keeps the mutex
    }
    
    sem_wait(&serfQueue);
    board(id);

    pthread_barrier_wait(&barrier_mutex);
    // barrier.wait();
    
    if (isCaptain){
        rowBoat(id);
        sem_post(&sem);
        // mutex.signal(); // captain releases the mutex
    }
}


void* hacker(void* arg){
    int id = (int) arg;  // Cast to int
    int isCaptain = 0;
    sem_wait(&sem);
    printf("Hacker %d is waiting on queue\n", id);
    hackers += 1;
    if (hackers == 4){
        printf("ALL HACKERS\n");
        // hackerQueue.signal(4);
        for (int i = 0; i < 4; i++){
            sem_post(&hackerQueue);
        }
        hackers = 0;
        printf("Hacker %d is captain\n", id);
        isCaptain = 1;
    }
    else if (hackers == 2 && serfs >= 2){
        printf("HACKER: METADE CADA!!\n");
        sem_post(&hackerQueue);
        sem_post(&hackerQueue);
        sem_post(&serfQueue);
        sem_post(&serfQueue);
        // hackerQueue.signal(2);
        // serfQueue.signal(2);
        serfs -= 2;
        hackers = 0;
        isCaptain = 1;
    }
    else {
        sem_post(&sem); // captain keeps the mutex
    }
    
    sem_wait(&hackerQueue);
    board(id);

    pthread_barrier_wait(&barrier_mutex);
    // barrier.wait();
    
    if (isCaptain){
        rowBoat(id);
        sem_post(&sem);
        // mutex.signal(); // captain releases the mutex
    }
}

#define NUM_THREADS 100
int main(){

    sem_init(&sem, 0, 1);
    sem_init(&hackerQueue, 0, 0);
    sem_init(&serfQueue, 0, 0);
    pthread_barrier_init(&barrier_mutex, NULL, 4);

    srandom(time(NULL));
    pthread_t threads[NUM_THREADS];
    for (int i = 0; i < NUM_THREADS; i++){
        if(rand() % 2 == 0){
            pthread_create(&threads[i], NULL, hacker, (void*) i);
        } else {
            pthread_create(&threads[i], NULL, serf, (void*) i);
        }
    }

    return 0;
}

