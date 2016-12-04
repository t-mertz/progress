import progress
import time
import multiprocessing
import sys

TIMEOUT = 5
SLEEP = 0.1

def sleep():
	time.sleep(SLEEP)
	return 0


if __name__ == "__main__":
	ncpus = 4
	N = 10*ncpus
	
	print("{0:14s}{1}".format("Version", progress.__version__))
	print("{0:14s}{1}".format("Platform", sys.platform))
	print("{0:14s}{1}".format("#Processes", ncpus))
	print("{0:14s}{1}\n".format("#Tasks", N))
	
	print("Testing single...\n")

	tracker = progress.Progress(N)

	for i in range(N):
		tracker.begin()
		sleep()
		tracker.record(1)

	tracker.report()

	print("\nTesting bundle...\n")

	tracker = progress.Progress(N)
	for i in range(N // ncpus):
		tracker.begin()
		for j in range(ncpus):
			sleep()
		
		tracker.record(ncpus)

	tracker.report()

	print("\nTesting multicore...\n")

	p = multiprocessing.Pool(ncpus)

	tracker = progress.Progress(N)

	try:
		for i in range(N // ncpus):
			tracker.begin()
			
			res = [p.apply_async(sleep) for j in range(ncpus)]
			
			res = [res[i].get(timeout=TIMEOUT) for i in range(ncpus)]
			
			tracker.record(ncpus)
	except multiprocessing.TimeoutError:
		p.close()
		p.terminate()
		p.join()
		raise multiprocessing.TimeoutError("Process did not " + 
			"respond within {} seconds.".format(TIMEOUT))
	except:
		p.close()
		p.terminate()
		p.join()
		raise
	finally:
		p.close()
		p.terminate()
		p.join()
			
	tracker.report()
	
	print("\nTest SUCCESS!")

	print("\nTesting Stopwatch:")

	with progress.Stopwatch() as w:
		sleep()
	
	#assert w.get_time() == SLEEP

	#print("Stopwatch returned " + str(w))