# ---
# test_makefile.sh - shell program which runs tests to verify ../Makefile functions correctly
# todo: fix stderr not indent printing
# todo: fix --binary should fail because stderr is not "^?"
# ---
PRG=make
TPRG=$(basename $0) # test_makefile.sh
echo "FULL NAME: $0"
CWD=$(pwd)
SUB_DIR=$(find . -name test_makefile.sh -exec dirname {} \;) # bin/tcmd directory
cd $SUB_DIR    # ./tests
SRC_DIR=$(pwd) # /../tests absolute path dir containing file test_makefile.sh
OUT_FILE=/tmp/${TPRG}_$$
teardown(){
  if [ -f "$OUT_FILE" ]; then rm -rf "$OUT_FILE"; echo "Note: rm -rf $OUT_FILE"; fi
  exit 
}
trap "TRAP=TRUE; teardown; exit 1" 1 2 3 15

TCMD_DIR=${SRC_DIR}/../bin
    TCMD=${TCMD_DIR}/tcmd.py

cd $SRC_DIR/.. # Dir which contains Makefile
source $SRC_DIR/../inc/test_utils.sh
print_header "$TPRG"

# ----
# Execute functional tests
(
  # ---
  # Test 
  $TCMD -v -c "Verify make buildpydoc" "$PRG buildpydoc" "^Pass:"
  $TCMD -c "Verify make" "$PRG" "ls.*cat.*tcmd_binary.*tcmd_python.*install"
  $TCMD -c "Verify make ls" "$PRG ls" "ls.*cat.*tcmd_binary.*tcmd_python.*install"
  $TCMD -c "Verify make install" "$PRG install" "pip install -r inc/requirements.txt"
  $TCMD -c "Verify make cat" "$PRG cat" "# Makefile - QA Makefile"
  $TCMD -v -e " INFO:.*INFO" -c "Verify make tcmd_binary" "$PRG tcmd_binary" "^Pass:"
  $TCMD -v -c "Verify make tcmd_python"                   "$PRG tcmd_python" "^Pass:"

) | tee $OUT_FILE 2>&1

# ----
# Count the passes and failures
print_test_counts "$OUT_FILE"

# ----
# Do some cleanup like removing $OUT_FILE
teardown
