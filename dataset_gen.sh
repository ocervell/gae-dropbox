echo -n "Generating 100 files of 1KB ... "
python random_gen.py 100 1024       #100 files of 1KB
echo "done."
echo -n "Generating 100 files of 10KB ... "
python random_gen.py 100 10240      #100 files of 10KB
echo "done."
echo -n "Generating 100 files of 100KB ... "
python random_gen.py 100 102400     #100 files of 100KB
echo "done."
echo -n "Generating 100 files of 1MB ... "
python random_gen.py 100 1048576     #100 files of 1MB
echo "done."

echo -n "Generating 10 files of 10MB ... "
python random_gen.py 10 10485760    #10 files of 10MB
echo "done."

echo -n "Generating 1 file of 100MB ... "
python random_gen.py 1 10485600     #1 file of 100MB
echo "done."
'''
