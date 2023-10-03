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



from django.http import HttpResponse
from django.views import View

def download_file(file_name):
    time.sleep(2)  # Simulate file download
    return f"Downloaded: {file_name}"

class DownloadView(View):
    def get(self, request):
        files = ["file1.txt", "file2.txt", "file3.txt"]
        responses = []

        # Create threads to download files concurrently
        threads = [threading.Thread(target=lambda f=file: responses.append(download_file(f))) for file in files]

        # Start the threads
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return HttpResponse("<br>".join(responses))
