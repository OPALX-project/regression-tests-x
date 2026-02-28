# regresion-test-x

## Purpose

Create and run OPALX regression tests is similar to the procedure for OPAL 
described [here](https://github.com/OPALX-project/regression-tests/tree/master).


## Create a Reference Solution

1. clone this repository for example into $HOME/git
2. checkout the branch *cleanup*
3. create a new directory *foo* in $HOME/git/regresion-test-x/RegressionTests with an inputfile *foo.in*
4. make sure OPALX_EXE_PATH is set and $HOME/git/regresion-test-x/bin is in the PATH
5. cd to $HOME/git/regresion-test-x/RegressionTests/foo and execute *makeReference.sh*
6. commit the directory to this repository in the branch *cleanup*

In case you need to run on multiple ranks use *--ranks number* argument on **makeReference.sh**
