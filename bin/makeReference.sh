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

# JSON files already in the test directory are inputs; only the ones the run writes are results
shopt -s nullglob
JSON_INPUTS=(*.json)
shopt -u nullglob

#
mpirun -np ${RANKS} ${OPALX_EXE_PATH}/opalx ${F} --info 10 | tee ${FB}.out

# collect output files (supports single and multi-container runs, and JSON results such as
# COF OUTPUT, which a .rt line "<file>.json <path> <eps>" compares)
OUT_FILE=${FB}.out
shopt -s nullglob
STAT_FILES=()
for SF in ${FB}.stat ${FB}_c*.stat; do
    [ -f "${SF}" ] && STAT_FILES+=("${SF}")
done
JSON_FILES=()
for JF in *.json; do
    [[ " ${JSON_INPUTS[*]} " == *" ${JF} "* ]] || JSON_FILES+=("${JF}")
done
shopt -u nullglob

if [ ${#STAT_FILES[@]} -eq 0 ] && [ ${#JSON_FILES[@]} -eq 0 ]; then
    echo "Error: no .stat or new .json files found for ${FB}"
    exit 1
fi

# a run without tracking (e.g. COF only) writes no timing.dat
REF_FILES=(${OUT_FILE} "${STAT_FILES[@]}" "${JSON_FILES[@]}")
[ -f timing.dat ] && REF_FILES+=(timing.dat)

#
mkdir -p reference
for RF in "${REF_FILES[@]}"; do
    cp ${RF} reference/
    cd reference
    md5sum ${RF} > ${RF}.md5
    cd ..
done

rm -rf data *.h5 *.out *.stat timing.dat "${JSON_FILES[@]}"
