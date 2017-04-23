cd ..
make clean
make
cd runs
../bin/CMPsim.usetrace.64 -threads 1 -t ../../traces/400.perlbench.out.trace.gz -o ls.stats -cache UL3:1024:64:16 -LLCrepl 0
