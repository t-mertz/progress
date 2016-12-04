
#ifndef __PROGRESS_H__
#define __PROGRESS_H__

#include <ctime>
#include <string>
#include <vector>
#include <cmath>
#include <sstream>
#include <iostream>

#define get_time() (static_cast<fptype> (std::clock()) / CLOCKS_PER_SEC)
#define PROGRESS_VERSION "Progress Ver. 0.01"

typedef double fptype; // does not print 100% if set to float

class Progress {
	static constexpr char* version = "Progress Ver. 0.01";

	/**
	 * Enum type describing the type of weight function used for
	 * determining the estimate for the remaining time.
	 */
public:
	enum weight {
		none,
		linear,
	};

private:
	// settings
	bool _print_remaining;
	int _ntasks;
	fptype _print_interval;
	weight _estimate_type;

	int _ntasks_complete;
	fptype _progress;
	std::vector<fptype> _times, _times_total;

	fptype _t_start, _t_stop, _t_last_stop;

	fptype remaining(weight);

public:
	Progress(int, fptype, bool, weight);
	Progress(int, fptype, bool);
	Progress(int);
	void begin();
	void record(int);
	fptype avg_tasks();
	fptype avg_total(weight);
	std::string remaining_str();
	fptype total();
	fptype total_tasks();
	std::string format_time(fptype);
	std::string format_time(fptype, std::string);
	void print();
	void report();

};


Progress::Progress(int ntasks, fptype print_interval, bool print_remaining) : 
		_ntasks(ntasks), _print_interval(print_interval), _print_remaining(print_remaining),
		_times(), _times_total(), _ntasks_complete(0), _progress(0.0), 
		_estimate_type(weight::none) {}

Progress::Progress(int ntasks, fptype print_interval, bool print_remaining, weight estimate_type) :
	_ntasks(ntasks), _print_interval(print_interval), _print_remaining(print_remaining),
	_times(), _times_total(), _ntasks_complete(0), _progress(0.0),
	_estimate_type(weight::none) {}

Progress::Progress(int ntasks) :
		_ntasks(ntasks), _print_interval(0.1), _print_remaining(true),
		_times(), _times_total(), _ntasks_complete(0), _progress(0.0),
		_estimate_type(weight::none) {}


/**
 * Set beginning of an interval.
 */
void Progress::begin() {

	fptype temp = static_cast<fptype>(std::clock()) / CLOCKS_PER_SEC;
	_t_start = temp;
	_t_stop = temp;
}

/**
 * Record time interval since the last call to begin() and print
 * progress according to print settings.
 *
 * int ntasks: number of tasks completed in that interval
 */
void Progress::record(int ntasks) {

	_t_last_stop = _t_stop;
	_t_stop = get_time();

	fptype time = (_t_stop - _t_start) / ntasks;
	fptype time_total = (_t_stop - _t_last_stop) / ntasks;
	for (int i = 0; i < ntasks; ++i) {
		_times.push_back(time);
		_times_total.push_back(time_total);
	}
	_ntasks_complete += ntasks;
	
	if (_print_interval != 0.0) {
		print();
	}

}

/**
 * Compute average time for one task.
 */
fptype Progress::avg_tasks() {

	fptype sum = 0.0;
	for (auto& time : _times) {
		sum += time;
	}
	return sum / _ntasks_complete;
}

/**
 * Compute the average time for one task based on the time passed
 * since the first call to begin(). Estimate is based
 * on the time needed for completed tasks and the given weight.
 *
 * weight weight: Progress::weight::none, Progress::weight::linear
 */
fptype Progress::avg_total(weight weight) {

	fptype sum = 0.0;
	if (weight == none) {
		for (auto& time : _times_total) {
			sum += time;
		}
		sum /= _ntasks_complete;
	}
	else if (weight == linear) {
		for (int i = 1; i <= _ntasks_complete; ++i) {
			sum += i * _times_total[i - 1];
		}
		sum /= 0.5 * (_ntasks_complete * (_ntasks_complete - 1));
	}
	else {
		throw 1, "Not Implemented";
	}

	return sum;
}

/**
 * Compute an estimate for the remaining time. Estimate is based
 * on the time needed for completed tasks and the given weight.
 *
 * weight weight: Progress::weight['none'], Progress::weight['linear']
 */
fptype Progress::remaining(weight weight) {

	return (_ntasks - _ntasks_complete) * avg_total(weight);
}

/**
 * Return remaining time as std::string.
 */
std::string Progress::remaining_str() {

	fptype rem_time = remaining(_estimate_type);
	return format_time(rem_time);
}

/**
 * Compute the total time between consecutive calls to begin(), record().
 */
fptype Progress::total() {

	fptype sum = 0.0;
	for (auto& time : _times) {
		sum += time;
	}
	return sum;
}

/**
 * Compute the total time since the first call to begin().
 */
fptype Progress::total_tasks() {

	fptype sum = 0.0;
	for (auto& time : _times_total) {
		sum += time;
	}
	return sum;
}

/**
 * Format time as Dd Hh Mm S.Ss. Outputs only up to last non-zero value.
 * E.g.: 174.2 --> 2m 54.2s
 */
std::string Progress::format_time(fptype time) {

	int d, h, m;
	float s;

	if (time >= 60) {
		m = int (time) / 60;
		s = std::fmod(time, 60);
		if (m >= 60) {
			h = m / 60;
			m = m % 60;
			if (h >= 24) {
				d = h / 24;
				h = h % 24;
			}
			else d = 0;
		}
		else h = 0;
	}
	else {
		s = time;
		d = 0;
		h = 0;
		m = 0;
	}

	std::string time_str = "";
	bool db = !(d == 0);
	bool hb = !(h == 0);
	bool mb = !(m == 0);
	//bool sb = !(s == 0.0);

	std::ostringstream osstrm;

	if (db) osstrm << d << "d ";
	if (hb) osstrm << h << "h ";
	if (mb) osstrm << m << "m ";
	
	std::cout.setf(std::ios::fixed, std::ios::floatfield);
	osstrm.precision(3);
	osstrm.width(4);
	osstrm.fill('0');
	osstrm << s << "s";
	
	return osstrm.str();
}

/**
 * Format time as Dd Hh Mm S.Ss. Overloaded method outputs only parts
 * declared in format_str.
 * E.g.: format_str = "dh", time = 18462 --> 0d 5.1h
 */
std::string Progress::format_time(fptype time, std::string format_str) {
	std::cout << "Not implemented" << std::endl;
	throw 1;
}

/**
 * Print current progress to stdout if settings permit.
 */
void Progress::print() {

	fptype progress = static_cast<fptype> (_ntasks_complete) / _ntasks;

	if (_progress <= progress) {
		std::ostringstream osstrm;
		osstrm.precision(3);
		osstrm.width(4);
		osstrm.fill(' ');
		osstrm << progress * 100 << "% complete.";

		if (_print_remaining) {
			osstrm << " " << remaining_str() << " remaining";
		}

		std::cout << osstrm.str() << std::endl;

		_progress += _print_interval;
	}
}

/**
 * Print summary to stdout.
 */
void Progress::report() {
	std::cout << "Total time passed: "
		<< format_time(total_tasks()) << std::endl
		<< "Average time for one task: "
		<< format_time(avg_tasks()) << std::endl;
}

#endif // __PROGRESS_H__