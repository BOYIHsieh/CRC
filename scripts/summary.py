import sys
import os
import re
import gzip

l = os.listdir('./')
l = [item for item in l if item[-2:] == "gz"]
l.sort()
lps = 0
mis = 0

lps0 = 0
mis0 = 0

lps1 = 0;
mis1 = 0

cnt = 0
cyc = 0
if True:
	print "| Benchmark | Miss Rate |"
	for x in l:
		print "| " + x[:-9] + ".out.trace.gz |",
		fin = gzip.open('./' + x)
		last_line = fin.read()
		tmp_cnt = re.search(r"ICOUNT: (\d*) C", last_line).group(1)
		tmp_cyc = re.search(r"CYC: (\d*) C", last_line).group(1)
		tmp_cpi = re.search(r"CPI: (\d*\.\d*) G", last_line).group(1)
		b = round(1.0 * float(tmp_cpi),6)
		print b,"|",
		cnt += int(tmp_cnt)
		cyc += int(tmp_cyc)

		#last_line = last_line[-500:]
		tmp_lps = re.search(r"Lookups: (\d*) M", last_line).group(1)
		tmp_mis = re.search(r"Misses: (\d*) M", last_line).group(1)
		b = round(100.0 * int(tmp_mis) / int(tmp_lps),6)
		print b,"|"
		lps += int(tmp_lps)
		mis += int(tmp_mis)
	print "| TOTAL |",round(1.0 * int(cyc) / int(cnt),6),"|",round(100.0 * int(mis) / int(lps),6),"|"

else:
	for x in l:
		print "| " + x[:-9] + ".out.trace.gz |",
		fin = gzip.open('../result/' + x)
		last_line = fin.read()[-500:]
		tmp_lps = re.search(r"Lookups: (\d*) M", last_line).group(1)
		tmp_mis = re.search(r"Misses: (\d*) M", last_line).group(1)
		#print tmp_lps,"|",tmp_mis,"|",round(100.0 * int(tmp_mis) / int(tmp_lps),2),"|"
		a = round(100.0 * int(tmp_mis) / int(tmp_lps),6)
		print a,"|",
		lps1 += int(tmp_lps)
		mis1 += int(tmp_mis)

		fin = gzip.open('../result0/' + x)
		last_line = fin.read()[-500:]
		tmp_lps = re.search(r"Lookups: (\d*) M", last_line).group(1)
		tmp_mis = re.search(r"Misses: (\d*) M", last_line).group(1)
		#print tmp_lps,"|",tmp_mis,"|",round(100.0 * int(tmp_mis) / int(tmp_lps),2),"|"
		a = round(100.0 * int(tmp_mis) / int(tmp_lps),6)
		print a,"|",
		lps0 += int(tmp_lps)
		mis0 += int(tmp_mis)

		fin = gzip.open('./' + x)
		last_line = fin.read()[-500:]
		tmp_lps = re.search(r"Lookups: (\d*) M", last_line).group(1)
		tmp_mis = re.search(r"Misses: (\d*) M", last_line).group(1)
		#print tmp_lps,"|",tmp_mis,"|",round(100.0 * int(tmp_mis) / int(tmp_lps),2),"|"
		b = round(100.0 * int(tmp_mis) / int(tmp_lps),6)
		if(b < a):
			print '**' + str(b) + "** |"
		else:
			print b,"|"
		lps += int(tmp_lps)
		mis += int(tmp_mis)
	print "average|",round(100.0 * int(mis1) / int(lps1),6),"|",round(100.0 * int(mis0) / int(lps0),6),"|",round(100.0 * int(mis) / int(lps),6),"|"
