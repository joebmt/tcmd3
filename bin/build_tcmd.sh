#!/bin/bash
# ---
# Run pyinstaller to create a binary tcmd from tcmd.py
# Note: 1. Must be in the ./bin directory for this script for pyinstaller to build correctly
# ---
PRG=$(basename $0)
CWD=$(pwd)
SUB_DIR=$(find . -name build_tcmd.sh -exec dirname {} \;) # bin/tcmd directory
cd $SUB_DIR    # ./bin
SRC_DIR=$(pwd) # /.../bin absolute path dir containing file tcmd.py

function usage(){
    echo "$PRG - build the tcmd program as a binary file or as a python file

    Usage: $PRG --python   ..... ln -s tcmd.py tcmd
           $PRG --binary   ..... call pyinstaller to build tcmd from tcmd.py
           $PRG -h         ..... this help message
"
}

if [[ -z "$1" ]]; then
    usage
    echo "Note: You must provide an argument" 
    exit
fi

# ---
# Process command line args
# ---
while [ $# -ne 0 ]; do
  case $1 in
    --python) TYPE=python
      shift
      ;;
    --binary) TYPE=binary
      shift
      ;;
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

# Create a sym link of tcmd.py --> tcmd and exit
if [ $TYPE = "python" ]; then
    if [ -f $SRC_DIR/tcmd ]; then
        echo "Note: rm -f $SRC_DIR/tcmd"
        rm -f $SRC_DIR/tcmd
    fi
    echo "Note: ln -s tcmd.py tcmd"
    ln -s $SRC_DIR/tcmd.py $SRC_DIR/tcmd

    # ---
    # Test that tcmd.py is linked to tcmd
    # ---
    echo "---"
    $SRC_DIR/tcmd.py -c "Verify tcmd is sym linked to tcmd.py" "ls -alt tcmd*" "tcmd -> .*/tcmd.py"
    exit 0
fi

# ---
# Verify pyinstaller installed
# ---
OUT=$(type pyinstaller); RET=$?
if [ $RET -ne 0 ]; then
    echo "Warn: Installing pyinstaller because it is not installed"
    pip install pyinstaller
fi

# ---
# Create dist/tcmd binary
# ---
PYTHON_VERSION=$(python --version 2>&1)
if echo "$PYTHON_VERSION" | grep "Python 3." >/dev/null 2>&1; then
    pyinstaller --hiddenimport _sysconfigdata --onefile tcmd.py
else
    echo "Note: Only python 3 is supported at this time.  Exiting ..."
    exit 1
fi

# ---
# Now cd back to CWD
# ---
cd $CWD

# ---
# mv the binary file dist/tcmd to ./tcmd.bin and remove ./dist and ./build dirs
# ---
if [ ${SRC_DIR}/dist/tcmd ]; then
    if test -f ${SRC_DIR}/dist/tcmd; then
        mv ${SRC_DIR}/dist/tcmd ${SRC_DIR}/tcmd.bin
        echo "Note: rm -rf ${SRC_DIR}/dist"
        rm -rf ${SRC_DIR}/dist
    fi
    if test -d ${SRC_DIR}/build/tcmd; then
        echo "Note: rm -rf ${SRC_DIR}/build"
        rm -rf ${SRC_DIR}/build
    fi
    echo "Note: rm -f ${SRC_DIR}/tcmd.spec"
    if test -f ${SRC_DIR}/tcmd.spec; then
        rm -f ${SRC_DIR}/tcmd.spec
    fi
fi

# ---
# Now rm and link the binary file tcmd.bin --> tcmd 
# ---
cd $SRC_DIR
if [ -f $SRC_DIR/tcmd ]; then
    rm -f $SRC_DIR/tcmd
fi
echo "Note: ln -s tcmd.bin tcmd"
ln -s $SRC_DIR/tcmd.bin $SRC_DIR/tcmd

# ---
# Test that tcmd.bin is linked to tcmd
# ---
echo "---"
$SRC_DIR/tcmd.py -c "Verify tmcd is sym linked to tcmd.bin" "ls -alt tcmd*" "tcmd -> .*/tcmd.bin"
cd $CWD
exit 0
