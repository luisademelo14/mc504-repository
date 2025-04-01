#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <atomic>
#include <barrier>

using namespace std;

constexpr int NUM_THREADS = 5;  // Number of threads (as an example)
int hackers = 0;
int serfs = 0;
int isCaptain = 0;

mutex mtx;
condition_variable hackerQueueCV;
condition_variable serfQueueCV;
mutex barrier_mutex;
int counter = 0;
int thread_count = 4;


thread workers[NUM_THREADS];

void board(int id) {
    // Simulate boarding process
    cout << id << " has boarded" << endl;
}

void rowBoat() {
    // Simulate rowing process
    cout << "Rowing boat with Captain" << endl;
}

void* hacker(void* arg) {
    int id = *(int*)arg;  // Cast to int
    cout << "Hacker " << id << " wants to board" << endl;
    
    unique_lock<mutex> lock(mtx);

    hackers += 1;
    cout << "Count: " << hackers << endl;


    if (hackers == 4) {
        // Signal 3 waiting threads (hackers)
        hackerQueueCV.notify_all();
        hackers = 0;
        isCaptain = 1;
        cout << "Hacker " << id << " is captain" << endl;
    }
    else if (hackers == 2 && serfs >= 2) {
        // Signal 1 hacker and 2 serfs to proceed
        hackerQueueCV.notify_one();
        serfQueueCV.notify_all();
        serfs -= 2;
        hackers = 0;
        isCaptain = 1;
    }
    else {
        cout << "Hacker " << id << " is waiting on queue" << endl;
        hackerQueueCV.wait(lock);  // Releases lock and wait until signaled
        cout << "Hacker " << id << " ACORDOU " << endl;
    }
    
    board(id);

    barrier_mutex.lock();
    counter++;
    cout << "Hacker " << id << " reached the barrier" << endl;
    cout << "Barrier counter: " << counter << endl;
    hackerQueueCV.notify_all();  // Notify all threads waiting on the barrier
    barrier_mutex.unlock();

    
    while(counter < thread_count); // Busy wait until all threads reach this point
     
    if (isCaptain) {
        rowBoat();
        isCaptain = 0;  // Reset captain status after rowing
    }

    return NULL;
}

int main() {
    int n_threads;
    cout << "Enter number of threads: ";
    cin >> n_threads;

    vector<thread> threads;
    for (int i = 0; i < n_threads; i++) {
        // Create and start threads
        workers[i] = thread(hacker, (void*) &i);
    }

    for (int i = 0; i < n_threads; i++) {
        workers[i].join();
    }

    return 0;
}
