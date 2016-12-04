# -*- coding: utf-8 -*-
"""
Copyright (c) 2015-2016 Thomas Mertz

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED 
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from __future__ import division, print_function # if pyversion < 3.0
import time
import lacommon
import sys, os
#import numpy as np

pyVERSION = float(sys.version[:3])

__version__ = '0.14'

class Progress:
	"""
	Log the progress of a calculation that is done in steps.
	The total number of tasks to be done is ntasks. Calling the method
	::func::begin before starting the calculation sets the time, after the
	calculation is done call ::func::record with the number of tasks completed
	to record the duration for each task.
	"""
	def __init__(self, ntasks, print_interval=0.1, print_remaining=True, filename='stdout'):
		"""
		ntasks: number of tasks to be computed in total\n
		print_interval: steps in which progress is to be printed. Set to None
		to disable printing.\n
		print_remaining: enable/disable printing of the remaining time
		"""
		
		if ntasks > 0:
			self._ntasks = int(ntasks)
		else:
			raise ValueError("ntasks must be positive.")
		
		if 0 < print_interval <= 1 or print_interval is None:
			self._print_interval = print_interval
		else:
			raise ValueError("print_interval must be in (0,1] or None.")
		
		if type(print_remaining) == bool:
			self._print_remaining = print_remaining
		else:
			raise TypeError("print_remaining must be boolean.")
		if self._print_remaining:
			self._len_rem_str = 0
		
		self._times = []
		self._times_total = []
		self._ntasks_complete = 0
		self._progress = 0
		self._timestamp = True
		self._filename = filename
	
	def begin(self):
		"""
		Set beginning of an interval.
		"""
		self._t_start = time.time()
		self._t_stop = time.time()
	
	def record(self, ntasks, cont=False):
		"""
		Record time interval since the last call to ::func::begin and print
		progress according to print settings.
		
		ntasks: number of tasks completed in that interval
		"""
		self._cont = cont 
		self._t_last_stop = self._t_stop
		self._t_stop = time.time()
		self._times += [(self._t_stop - self._t_start) / ntasks] * ntasks
		self._times_total += [(self._t_stop - self._t_last_stop) \
								/ ntasks] * ntasks
		self._ntasks_complete += ntasks
		
		if self._print_interval is not None:
			self.print()
		
	def avg_tasks(self):
		"""
		Return the average time between two consecutive calls to func::begin 
		and func::recod, i.e. average time for one single task.
		"""
		return sum(self._times) / self._ntasks_complete
		
	def avg_total(self):
		"""
		Return the average time between two calls to func::record. Includes
		overhead created by loops and other maintenance calls.
		"""
		return sum(self._times_total) / self._ntasks_complete
		
	def remaining(self, weight='none'):
		"""
		Return an estimate for the remaining time in seconds.
		
		weight (optional): string specifying the weight distribution of
		each task taken into account for the remaining time estimate. default
		is 'none': uniform weight distribution. 'linear': linear weight 
		distribution.
		"""
		if weight == 'none':
			if not self._cont:
				return (self._ntasks - self._ntasks_complete) * self.avg_total()
			else:
				return (self._ntasks - self._ntasks_complete) * self.avg()
		elif weight == 'linear':
			if not self._cont:
				dist_func = [i * self._times_total[i-1] \
							/ sum(range(1,self._ntasks_complete+1)) \
							for i in range(1,self._ntasks_complete+1)]
			else:
				dist_func = [i * self._times[i-1] \
							/ sum(range(1,self._ntasks_complete+1)) \
							for i in range(1,self._ntasks_complete+1)]
			return (self._ntasks - self._ntasks_complete) * sum(dist_func)
		else:
			raise NotImplementedError
		
	def remaining_str(self, formatter_str=''):
		"""
		Return an estimate for the remaining time in a formatted string.
		
		formatter_str: string of type 'dhms', where 'd': days, 'h' hours,
		'm': minutes, 's': seconds. Return argument contains only information
		specified in formatter_str.
		"""
		rem_time = self.remaining('linear')
		return lacommon.format_time(rem_time, formatter_str)
		
	def total(self):
		"""
		Return the total time passed since the first call to func::begin.
		"""
		return sum(self._times_total)
		
	def total_tasks(self):
		"""
		Return the total time needed for all tasks.
		"""
		return sum(self._times)
		
	def print(self):
		"""
		Print progress to file.
		"""
				
		progress = self._ntasks_complete / self._ntasks
		assert 0 <= progress <= 1
		
		if self._progress < progress:
			out_string = "{0:2.0f}% {1}complete.".format(progress*100, (1-int(progress))*" ")
			#if progress < 1: out_string += " "
			
			if self._print_remaining:
				rem_str = self.remaining_str()
				if len(rem_str) > self._len_rem_str:
					self._len_rem_str = len(rem_str)
				out_string += " {{0:>{0}s}} {{1}}".format(self._len_rem_str).format(rem_str, "remaining.")
			
			if self._timestamp:
				out_string += " # {}".format(time.strftime("%m/%d/%y %I:%M:%S %p"))
			
			self._to_file(out_string, filename=self._filename)
			
			self._progress += self._print_interval
			
	def _to_file(self, out_str, file=sys.stdout, filename='stdout'):
		"""
		Write out_str to file (default is stdout).
		
		out_str: string/printable to be written.
		file (optional): file object with write access
		filename (optional): name of file to which progress is printed.
			default is `stdout`.
		"""
		if filename != 'stdout':
			try:
				file = open(filename, 'a', buffering=0)
			except IOError:
				raise IOError("IOError while opening file {} in Progress.".format(filename))
		
		try:
			file.flush()
			print(out_str, file=file)
			file.flush()
		except IOError:
			raise IOError("IOError while printing to {} in Progress. ".format(file) + \
				"Are you sure you have write access?")
			
		if filename != 'stdout':
			file.close()
			
	def report(self):
		"""
		Print report to file, summarizes total and average time.
		"""
		out_str = "\nREPORT:\n"
		out_str += "{0:20s}{1}\n" + "{2:20s}{3}"
		out_str = out_str.format("Total time passed:", lacommon.format_time(self.total(), ''), \
								 "Avg. time per task:", lacommon.format_time(self.avg_tasks(), ''))
		self._to_file(out_str, filename=self._filename)



class Timer(object):
	"""
	Measures time between calls to set_initial() and set_final().
	"""

	def __init__(self):
		self._t0 = self._t1 = None
	
	def set_initial(self):
		self._t0 = time.time()
	
	def set_final(self):
		self._t1 = time.time()

	def get_time(self):
		return (self._t1 - self._t0)
	
	def __str__(self):
		return str(self.get_time())


class Stopwatch(Timer):
	"""
	Measures time between calls to __enter__() and __exit__() and prints
	to file.
	"""

	def __init__(self, file=None):
		Timer.__init__(self)
		if file is None:
			self.file = sys.stdout
		else:
			self.file = outfile

	def __enter__(self):
		self.set_initial()
	
	def __exit__(self, type, value, traceback):
		self.set_final()
		print(self.get_time(), file=self.file)

		if type is None:
			return True
		else:
			return False