make
mkdir traces-debranch
for i in $(seq 1 20); do
    echo "[+] Recording trace ${i}"
    python3 ../../branch-tracer/branch-tracer.py example 0 "traces-debranch/trace${i}.txt" --verbose=OFF
done
python3 ../rewrite.py --rewrite-type DEBRANCH example example-debranch traces-debranch

valgrind ./example >> example.log
valgrind ./example-debranch >> example-debranch.log

diff example.log example-debranch.log

rm example.log example-debranch.log
make clean
rm -rf traces-debranch