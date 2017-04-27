'''
cd ..
make clean
make
cd runs
../bin/CMPsim.usetrace.64 -threads 1 -t ../../traces/400.perlbench.out.trace.gz -o ls.stats -cache UL3:1024:64:16 -LLCrepl 0

../CRC/bin/CMPsim.usetrace.64 -threads 1 -t ../traces/453.povray.out.trace.gz -o ls.stats -cache UL3:1024:64:16 -LLCrepl 2
'''
import sys
import os
import re
import gzip
import datetime

l = os.listdir(sys.argv[1])
l.sort()
time_result = []
for x in l:
	m = re.match(r"(\d{3}\..*)\.out\.trace\.gz", x)
	xx = sys.argv[1] + x
	if(m):
		name = m.group(1)
		tmp = '../bin/CMPsim.usetrace.64 -threads 1 -t ' + xx + ' -o ' + sys.argv[2] + name +'.stats -cache UL3:1024:64:16 -LLCrepl ' + sys.argv[3]
		print tmp
		start_time = datetime.datetime.now()
		os.system(tmp)
		s = datetime.datetime.now() - start_time
		t = int((1e6 * s.seconds + s.microseconds)) * 1e-6
		time_result.append((x,round(t,3)))

for item in time_result:
	print item