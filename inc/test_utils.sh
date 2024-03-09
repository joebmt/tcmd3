# ---
# test_utils.sh - shell utility functions for running functional tests with tcmd
# ---
LINE_WRAP=80

# ---
# indent() - Indent text same amount as tcmd does
# ---
function indent() { sed 's/^/      /'; }

# ---
# wrapline() - Indent text same amount as tcmd does but keep words together if possible
# ---
wrapline() { fold -w $LINE_WRAP -s | indent; }

# ---
# print_header() - Output the test program name to stdout
# ---
function print_header()
{
    PRG_NAME="$1"
    echo "---"
    echo "Test: $PRG_NAME"
    echo "---"
}

# ---
# print_test_counts() - Count the Pass and Fails of a test output file generated using tcmd
# ---
function print_test_counts()
{
    TEST_OUTPUT_FILE="$1"
    if [ ! -f "$TEST_OUTPUT_FILE" ]; then 
        echo "Warn: file [$TEST_OUTPUT_FILE] does not exist.  Not printing out test counts."
        return 1
    fi

    # ----
    # Count the passes and failures
    PASSES=$(grep "^Pass:" $OUT_FILE 2>/dev/null)
    FAILS=$( grep "^Fail:" $OUT_FILE 2>/dev/null)
    PCNT=$(  echo "$PASSES" | grep -c . 2>/dev/null | xargs echo)
    FCNT=$(  echo "$FAILS"  | grep -c . 2>/dev/null | xargs echo)
    TOTAL=$(($PCNT+$FCNT))
    TEST_PRG_NAME=$(basename $TEST_OUTPUT_FILE)
    echo "---"
    echo "Test Summary: $TEST_PRG_NAME"
    echo "---"
    echo "Passes: $PCNT"
    echo " Fails: $FCNT"
    echo " Total: $TOTAL"
    echo "---"
}
