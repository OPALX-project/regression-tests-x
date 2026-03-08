#!/bin/bash -l 

# check if we can run
if [ -z "${OPALX_EXE_PATH+x}" ]; then
    echo "Error: OPALX_EXE_PATH is not defined."
    exit 1
fi

# now many ranks we use
RANKS=1   # default
while [ $# -gt 0 ]; do
    case "$1" in
        --ranks)
            if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
                RANKS="$2"
                shift 2
            else
                echo "Error: --ranks requires a positive integer argument"
                exit 1
            fi
            ;;
        *)
            shift
            ;;
    esac
done
#echo "Using ranks = $RANKS"

#
F=`ls *.in`
FB=`basename -s ".in" $F`

# make the FB.local file
cat > ${FB}.local << EOF
#!/bin/bash
cd "\$(cd "\$(dirname "\$0")" && pwd)"
mpirun -np ${RANKS} "\$OPALX_EXE_PATH/opalx" ${F} --info 2 "\$@" 2>&1
EOF
chmod +x ${FB}.local

#
mpirun -np ${RANKS} ${OPALX_EXE_PATH}/opalx ${F} --info 10 | tee ${FB}.out
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
