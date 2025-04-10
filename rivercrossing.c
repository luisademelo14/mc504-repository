#include <pthread.h>
#include <semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int hackers = 0;
int serfs = 0;
int isCaptain = 0;
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
    printf("%d Rowing boat with Captain...\n", id);
    sleep(1); // Simulate time taken to row
}


void* hacker(void* arg){
    int id = *(int*)arg;  // Cast to int
    
    printf("Hacker %d wants to board\n", id);
    sem_wait(&sem);
    hackers += 1;
    if (hackers == 4){
        // hackerQueue.signal(4);
        for (int i = 0; i < 4; i++){
            sem_post(&hackerQueue);
        }
        hackers = 0;
        printf("Hacker %d is captain\n", id);
        isCaptain = 1;
    }
    else if (hackers == 2 && serfs >= 2){
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
    printf("Hacker %d is waiting on queue\n", id);
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

int main(){

    printf("Enter number of threads: ");
    int n_threads = scanf("%d", &n_threads);
    sem_init(&sem, 0, 1);
    sem_init(&hackerQueue, 0, 4);
    sem_init(&serfQueue, 0, 4);
    pthread_barrier_init(&barrier_mutex, NULL, n_threads);

    pthread_t threads[n_threads];
    for (int i = 0; i < n_threads; i++){
        pthread_create(&threads[i], NULL, hacker, (void*)&i);
    }

    return 0;
}

