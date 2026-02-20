# regresion-test-x

## Purpose

Create and run OPALX regression tests is similar to the procedure for OPAL 
described [here](https://github.com/OPALX-project/regression-tests/tree/master).


## Create a Reference Solution

1. run the simulation in an isolated directory
2. execute the script below
3. commit the directory to the repository

```
#
F=`ls *.in`
FB=`basename -s ".in" $F`
F1=`ls $FB.out`
F2=`ls $FB.stat`
F3=`ls $FB.lbal`
#
mkdir -p reference
cp $F1 reference/
cp $F2 reference/
cp $F3 reference/
#
cd reference
md5sum $F1 > $F1.md5
md5sum $F2 > $F2.md5
md5sum $F3 > $F3.md5
```
