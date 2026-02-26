# regresion-test-x

## Purpose

Create and run OPALX regression tests is similar to the procedure for OPAL 
described [here](https://github.com/OPALX-project/regression-tests/tree/master).


## Create a Reference Solution

1. create a isolated directory with an inputfile (yourfilename.in)
2. execute the script below and make sure OPAL_EXE_PATH is set
3. copy xxx.local and modyfiy
4. commit the directory to this repository in the branch *cleanup*

```
#!/bin/bash -l 
F=`ls *.in`
FB=`basename -s ".in" $F`
${OPAL_EXE_PATH}/opalx ${F} --info 10 | tee ${FB}.out
F1=`ls $FB.out`
F2=`ls $FB.stat`
#F3=`ls $FB.lbal`
#
mkdir -p reference
cp $F1 reference/
cp $F2 reference/
#cp $F3 reference/
#
cd reference
md5sum $F1 > $F1.md5
md5sum $F2 > $F2.md5
#md5sum $F3 > $F3.md5
cd ..
rm -rf data *.h5 *.out *.stat


```
