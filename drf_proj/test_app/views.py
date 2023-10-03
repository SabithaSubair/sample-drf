from django.shortcuts import render
# Create your views here.
import threading
import time

# Define a function that will run in a separate thread
def print_numbers():
    for i in range(1, 6):
        print(f"Number {i}")
        time.sleep(1)  # Sleep for 1 second between prints

def print_letters():
    for letter in 'ABCDE':
        print(f"Letter {letter}")
        time.sleep(1)  # Sleep for 1 second between prints

# Create two thread objects
thread1 = threading.Thread(target=print_numbers)
thread2 = threading.Thread(target=print_letters)

# Start the threads
thread1.start()
thread2.start()

# Wait for both threads to finish
thread1.join()
thread2.join()

print("Both threads have finished.")


