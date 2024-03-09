#!/bin/bash
# ---
# functions.sh - include file of functions for shell program
#   Note: 1. These are to be source into another shell program.
#            Ex: prg.sh: source functions.sh (does not run unit test below)
#         2. Unit tests at the bottom of script will run only if this program (function.sh) 
#            is called directly (not included inside a program).
#            Ex: functions.sh (runs all unit tests below)
# ---
# DBG=true
# if [ "$DBG" = true ]; then echo "Note: Start: set -xv"; set -xv; fi

function add()
{
    # if [ "$DBG" = true ]; then echo "Note: Inside add()"; set -xv; fi
    NUM1=$1
    NUM2=$2
    RESULT=$(($1+$2))

    echo "add $NUM1 + $NUM2 = $RESULT"
    return $RESULT
}

function multiply()
{
    # if [ "$DBG" = true ]; then echo "Note: Inside multiply()"; set -xv; fi
    NUM1=$1
    NUM2=$2
    RESULT=$(($1*$2))

    echo "multiply $NUM1 * $NUM2 = $RESULT"
    return $RESULT
}

function something_without_a_return()
{
    # if [ "$DBG" = true ]; then echo "Note: Inside something_without_a_return()"; set -xv; fi
    echo "Inside something_without_a_return()"
    rm -f /tmp/a /tmp/b
    touch /tmp/a
    cp /tmp/a /tmp/b
    rm -f /tmp/a
}

# ---
# Unit Tests: Will only run if called via functions.sh standalone
(
    [[ "${BASH_SOURCE[0]}" == "${0}" ]] || exit 0
    echo ---
    echo "Note: Executing ${BASH_SOURCE[0]} unit tests"
    echo ---
    PASS_CNT=0
    FAIL_CNT=0

    # ---
    # Utility Test Functions for unit tests
    function assertEquals()
    {
        MSG=$1; shift
        EXPECTED=$1; shift
        ACTUAL=$1; shift
        # /bin/echo -n "$MSG: "
        if [ "$EXPECTED" != "$ACTUAL" ]; then
            echo "Fail: EXPECTED=[$EXPECTED] ACTUAL=[$ACTUAL]"
            return 1
        else
            echo "Pass: $MSG"
            return 0
        fi
    }

    function addcnt()
    {
        # if [ "$DBG" = true ]; then echo "Note: Inside addcnt()"; set -xv; fi
        # set -xv
        RETURN_CODE=$1
        # echo "Note: addcnt(): RETURN_CODE: $RETURN_CODE"
        if [ $RETURN_CODE -eq 0 ]; then 
            PASS_CNT=$((PASS_CNT+1))
        else
            FAIL_CNT=$((FAIL_CNT+1))
        fi
        # set +xv
    }

    function print_results()
    {
        echo "---"
        echo "Total Pass: $PASS_CNT"
        echo "Total Fail: $FAIL_CNT"
        echo "Total Cnt : $(($PASS_CNT+$FAIL_CNT))"
    }

    function verify_something_without_a_return()
    {
        if [ "$DBG" = true ]; then echo "Note: Inside verify_something_without_a_return()"; : ; fi
        something_without_a_return
        if [ -f "/tmp/b" ]; then
          echo "Pass: something_without_a_return()"
          return 0
        else
          echo "Fail: something_without_a_return(): /tmp/b does not exist"
          return 1
        fi
    }

    # ---
    # Start of unit tests

    OUT=$(add 2 3); OUT_RET=$?
    assertEquals "add 2 3: adding two numbers" 5 $OUT_RET; RET=$?
    addcnt $RET

    OUT=$(multiply 2 3); OUT_RET=$?
    assertEquals "multiply 2 3: multiply two numbers" 6 $OUT_RET; RET=$?
    addcnt $RET

    OUT=$(verify_something_without_a_return); RET=$?
    addcnt $RET

    print_results
)
