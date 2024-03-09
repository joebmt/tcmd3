#!/bin/bash
# ---
# Run tcmd --pydoc to create ./pydoc/tcmd.html and then mv ../pydoc/tcmd.html
# Note: 1. Must be in the ./bin directory for this script for pydoc to build correctly
# ---
PRG=$(basename $0)
CWD=$(pwd)
SUB_DIR=$(find . -name build_pydoc.sh -exec dirname {} \;) # bin/tcmd directory
cd $SUB_DIR    # ./bin
SRC_DIR=$(pwd) # /.../bin absolute path dir containing file tcmd.py

function usage(){
    echo "$PRG - build the tcmd.py pydoc tcmd.html file 

    Usage: $PRG --python   ..... ln -s tcmd.py tcmd
           $PRG --binary   ..... call pyinstaller to build tcmd from tcmd.py
           $PRG -h         ..... this help message
"
}

# ---
# Process command line args
# ---
while [ $# -ne 0 ]; do
  case $1 in
    -h)
      usage;
      exit 0;
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

# ---
# Test that tcmd.py is linked to tcmd
# ---
echo "---"

# ---
# Test tcmd with tcmd
OUT=$($SRC_DIR/tcmd.py --pydoc date .)
echo "$OUT" | tcmd  --stdin : "Wrote tcmd.html"
# echo "Srcdir: $SRC_DIR"
# echo "Subdir: $SUB_DIR"
# echo "CWD: $CWD"

if test -f ${SRC_DIR}/pydoc/tcmd.html; then
    tcmd "mv ${SRC_DIR}/pydoc/tcmd.html ${SRC_DIR}/../pydoc/." ''
    rm -rf ${SRC_DIR}/pydoc
fi
tcmd -r 1 "test -d ${SRC_DIR}/pydoc" ""

if test -f ${SRC_DIR}/tcmd.pyc; then
    rm -f ${SRC_DIR}/tcmd.pyc
fi
tcmd -r 1 "test -f ${SRC_DIR}/tcmd.pyc" ""

exit 0
