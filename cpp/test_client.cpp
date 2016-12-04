/* Copyright (c) 2015 Thomas Mertz
 * 
 * Test client for the Progress class.
 * Sleeps N times for 10 milliseconds to test the progress output
 * and the remaining time estimate.
 */
#include "progress.cpp"

#include <cstdlib>// std::atoi
#include <thread> // std::this_thread::sleep_for
#include <chrono> // std::chrono::milliseconds
#include <iostream> //std::cout, std::endl

int main(int argc, char* argv[]) {

	int N; // number of iterations

	if (argc == 1) 
		N = 1000;
	else 
		N = std::atoi(argv[1]);

	Progress tracker(N, 0.1, true); // initialize tracker object
									// N tasks, print progress every 10%
									// print remaining time

	Progress tracker1(N, 0.1, true, Progress::weight::linear); // same as above
															   // but uses linear
															   // distribution to
															   // determine the estimate
	for (int i = 0; i < N; ++i) {

		tracker.begin(); // start the clock
		std::this_thread::sleep_for(std::chrono::milliseconds(10));
		tracker.record(1); // record time for 1 task
	}
	
	tracker.report(); // report summary

	// wait for user to finish program
	std::string dump;
	std::cin >> dump;
}