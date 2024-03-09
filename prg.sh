# ---
# prg.sh - shell program template
# ---
PRG=$(basename $0)
CWD=$(pwd)
TMPFILE=/tmp/${PRG}_$$
trap "TRAP=TRUE; teardown" 1 2 3 15
function teardown(){ if [ -f $TMPFILE ]; then rm -f $TMPFILE; fi }

# ---
# Load the functions used in this program here
source ${CWD}/inc/prg_functions.sh

# ---
# Give a usage message
function usage ()
{
  echo "
 $PRG: add or multiply two integers

    Usage: $PRG [-h] -add <int1> <int2>
           $PRG [-h] -multiply <int1> <int2>

  Options:

    -add <int1> <int2> ........ add the two integers and return the answer
    -multiply <int1> <int2> ... multiply the two integers and return the answer
    -h ........................ this help message

 Examples:

     $PRG -add 2 3 ............ add 2+3 and return 5
     $PRG -multiply 2 3 ....... multiply 2*3 and return 6
     $PRG -h .................. give help message
  "
}

# ----------------------------------------------------------------------------
# Process command-line arguments
if [[ -z "$1" ]]; then
  usage;
  echo "  Error: You must provide an argument!"
  exit 1
fi
while [ $# -ne 0 ]; do
  case $1 in
    -add) ACTION=add
      shift
      if [ $# -ne 2 ]; then
	     echo "Error: You must provide two integers with the -add option!"
	     usage
         exit 1
      fi
      INT1="$1"
      INT2="$2"
      shift; shift
      ;;
    -multiply) ACTION=multiply
      shift
      if [ $# -ne 2 ]; then
	     echo "Error: You must provide two integers with the -multiply option!"
	     usage
         exit 1
      fi
      INT1="$1"
      INT2="$2"
      shift; shift
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

# ---
# Execute the add or multiply
$ACTION $INT1 $INT2; RET=$?

# add 2 3; RET=$?
# echo "     add 2 3: $RET"
# multiply 2 3; RET=$?
# echo "multiply 2 3: $RET"
# something_without_a_return

# ---
# Execute any teardown commands and exit with the proper return status 
teardown
exit $RET
