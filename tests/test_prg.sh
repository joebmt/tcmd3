# ---
# test_prg.sh - shell program which runs tests to verify ../prg.sh functions correctly
# ---
    PRG="prg.sh"
   TPRG=$(basename $0) # test_prg.sh
    CWD=$(pwd)         # ../tests or ./tests
 SUB_DIR=$(find . -name test_prg.sh -exec dirname {} \;) # usually '.' dir or './tests'
 cd $SUB_DIR    # Now we are inside test_prg.sh dir
 SRC_DIR=$(pwd) # /../tests absolute path dir containing file test_prg.sh
OUT_FILE=/tmp/${TPRG}_$$
teardown(){
  if [ -f "$OUT_FILE" ]; then rm -rf "$OUT_FILE"; echo "Note: rm -rf $OUT_FILE"; fi
  exit 
}
trap "TRAP=TRUE; teardown; exit 1" 1 2 3 15

TCMD_DIR=${SRC_DIR}/../bin
    TCMD=${TCMD_DIR}/tcmd.py

# ----
# Source in utility functions
source $SRC_DIR/../inc/test_utils.sh

# ----
# Print a test header with the name of this test file
print_header "$TPRG"

# ----
# Execute functional tests
(
  cd ..
  # ---
  # Test the usage message -h option (Note: Have to backslash the square brackets since regex metachar
  $TCMD "$PRG -h" "Usage: prg.sh \[-h\] -add <int1> <int2>"

  # ---
  # Test the usage message -h option (Note: Have to use . for any char because '[]' are metachars
  $TCMD "$PRG -h" "Usage: prg.sh .-h. -add <int1> <int2>"

  # ---
  # Test the -add option with return code of 5 and stdout message
  # Note: '+' is a regex metachar so either have to backslash or use -b option
  $TCMD -v -r 5 "prg.sh -add 2 3" "add 2 \+ 3 = 5"

  # ---
  # Same test as above but using -b to backslash the regex
  # Note: '+' is a regex metachar so either have to backslash or use -b option
  $TCMD -v -b -r 5 "prg.sh -add 2 3" "add 2 + 3 = 5"

  # ---
  # Test the -multiply option with return code of 6 and stdout message
  # Note: '*' is a regex metachar so either have to backslash or use -b option
  $TCMD -v -r 6 "prg.sh -multiply 2 3" 'multiply 2 \* 3 = 6'

  # $TCMD -v $PRG "something_without_a_return"
  cd $CWD
) | tee $OUT_FILE 2>&1

# ----
# Count the passes and failures
print_test_counts "$OUT_FILE"

# ----
# Do some cleanup like removing $OUT_FILE
teardown
