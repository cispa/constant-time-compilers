make
mkdir traces-spec
for i in $(seq 1 10); do
    echo "[+] Recording trace ${i}"
    python3 ../../branch-tracer/branch-tracer.py example "${i}" "traces-spec/trace${i}.txt" --verbose=OFF
done

rm -rf rewrite-spec
python3 ../rewrite.py --rewrite-type SPEC example rewrite-spec traces-spec

chmod +x rewrite-spec/*

for file in rewrite-spec/*; do 
    valgrind $file 0;
done

make clean
rm -rf traces-spec rewrite-spec