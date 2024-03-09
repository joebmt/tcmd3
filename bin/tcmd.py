#!/usr/bin/env python
# ---
#   tcmd - test a commands output against a regular expression
# ---
#   Usage: tcmd [Options] cmd regEx
#
#            ====================================================================
#            cmd      ........... cmd to execute and test stdout, stderr, exit status
#            regEx    ........... regular expression to test the expected stdout of
#                                 the command
#            ====================================================================
# ---
#   Examples:
#
#     tcmd date 2018          ... same as: date | grep -i 2018
#
#     tcmd -c "date test" date 2018
#                             ... date | grep -i 2018 with a comment added to Pass/Fail lines
#
#     date | tcmd -s -c "cmd=date via --stdin" : 2018
#                             ... same as line above only using stdin and not testing return_code and stderr
#
#     tcmd -n date 2016       ... date | grep -v 2016 (negate regEx test=Pass)
#
#     tcmd -d 'cat /etc/hosts' '#|localhost'
#                             ... cat /etc/hosts | egrep -i "#|localhost"
#
#     tcmd -d -v date 2018    ... turn on debug and verbose output and check date cmd against regex 2018
#
#     tcmd -v "touch myfile; test -f myfile && rm -f myfile"  ""
#                             ... sting multiple commands together with ';' or && or ||
#
#     OUT=$(cat /etc/hosts)
#     echo "$OUT" | tcmd --stdin -v -c "bash variable test" : localhost
#                             ... echo "$OUT" | grep -i localhost (uses a bash variable w/--stdin)
#
#     OUT=$(tcmd ping -c 2 localhost); RET=$?
#     if [ $RET -eq 0 ] && echo "tcmd returned 0" || echo "tcmd did not return 0"
#                             ... how to run tcmd and capturing just PASS (0) or FAil (1) return code without
#                             ... printing tcmd output to stdout
#
#     tcmd -h                 ... this help message
#
# ---
#   Notes:
#
#     1. You can specify regEx as "", "^$", or "\A\z" for the empty string
#     2. regex matches re.MULTILINE and re.DOTALL (matches across multilines with ".")
#     3. This program only tested on python 2.7
#     4. This program requires textwrap and click python modules to be installed
#        Run: 'pip install -r inc/requirements.txt' to install these two modules
#     5. See tests/test_tcmd.sh for more examples of syntax
#
#   Warning:
#     1. You have to backslash regular expression meta chars on command line if you want them
#        to be interpreted as literal characters in the regex
#        (tcmd does not escape the metachars for you unless you use the --backslash option)
#        For example, use:
#          tcmd -v 'echo "add x+y"' "add x\+y"
#                                        (^ backslashed the '+' regex metachar)
#            instead of
#          tcmd -v 'echo "add x+y"' "add x+y"
#        Python regex metachars:
#          \       Escape special char or start a sequence.
#          .       Match any char except newline, see re.DOTALL
#          ^       Match start of the string, see re.MULTILINE
#          $       Match end of the string, see re.MULTILINE
#          []      Enclose a set of matchable chars
#          R|S     Match either regex R or regex S.
#          ()      Create capture group, & indicate precedence
#          *       0 or more. Same as {,}
#          +       1 or more. Same as {1,}
#          ?       0 or 1. Same as {,1}
#
# Options:
#   -d, --dbg                 Turn debug output on
#   -e, --error <text>        Stderr compared to regex
#   -n, --negate              Opposite (negate) regex operator like grep -v
#   -c, --comment <text>      Add a comment to Pass/Fail lines
#   -s, --stdin               Pipe stdin as cmd subsitute with :
#   -r, --return_code <text>  The return status compared to regex
#   -v, --verbose             Turn verbose output on
#   -p, --pydoc               Generate pydoc
#   -t, --timer               Report Execution time in seconds
#   -b, --backslash           Backslash all regex meta chars
#   -m, --min                 Print only minimum one line Pass or Fail except if
#                             --dbg
#   -h, --help                This usage message
#
# Author:
#   Joe Orzehoski
#
# License:
#   See readme.md file using Apache 2.0 License
# ---
# Todo:
#   1. Add stdin error with negate option
#   2. Add a return of 1 or 0 inside tests/t*.sh
#   3. Make tcmd into a module so it can be installed (use setup.py)
# ---

import traceback
import click
import pydoc
import sys
from sys import exit
import os
import subprocess
# Do not use re because of known issues.  Have to pip install regex.
# See: https://stackoverflow.com/questions/7063420/perl-compatible-regular-expression-pcre-in-python
# import re
import regex as re
import textwrap
from time import time as timetime
from datetime import *

# ---
# Define the DBG flag (can turn on via -d option or export DBG=true
DBG=0


def create_pydocs():
    """
    create_pydocs() - generate pydoc inside a directory pydocs in the current directory
    :return: None
    """
    pydoc_dir = 'pydoc'
    module = os.path.basename(__file__)[:-3] # Get the current filename and take off the '.py' extension
    # module = os.path.basename(__file__)  # Get the current filename
    print (os.path.basename(__file__))
    # exit(1)
    __import__(module)
    if not os.path.exists(pydoc_dir):
        os.mkdir(pydoc_dir)

    # ---
    # Write out the pydoc of this module to the pydoc/<module>.py file
    cwd = os.getcwd()
    os.chdir(pydoc_dir)
    pydoc.writedoc(module)
    os.chdir(cwd)


def indent(text, nspaces, ch=' '):
    """
    Indent every line of the text string nspaces

    :param text:    Text string to be indented nspaces amount
    :param nspaces: Amount spaces to indent
    :param ch:      The space char or another char to prepend to the indent
    :return:        The new indented string
    """
    padding = nspaces * ch
    padded_lines_list = [padding+line for line in text.splitlines(True)]
    return ''.join(padded_lines_list)


def pindent(msg, nspaces=6, line_width=180):
    """
    Prints every line of the text msg indented nspaces

    :param msg:        The text string to be indented nspaces amount
    :param nspaces:    Amount of spaces to indent
    :param line_width: Not used anymore
    """
    msg = str(msg)
    click.echo(indent(msg, nspaces))
    return

    # body = '\n'.join(['\n'.join(textwrap.wrap(line, 120,
    #                               break_long_words=False, replace_whitespace=False))
    #                   for line in msg.splitlines() if line.strip() != ''])
    # newmsg = textwrap.fill(msg, replace_whitespace=False, width=line_width, initial_indent=' '*nspaces, subsequent_indent=' '*nspaces)
    # print body
    # click.echo(newmsg)


def _runcmd(cmd, shell=True):
    """
    Executes a shell command in a subprocess and captures stdout, stederr, and return status

    Src: https://stackoverflow.com/questions/7353054/running-a-command-line-containing-pipes-and-displaying-result-to-stdout

    :param cmd:   shell command to run
    :param shell: subprocess.Popen(..., shell=True) to run commands with pipes
    :return:      tuple = (cmd_stdout, cmd_stderr, cmd_return)
    """
    global DBG

    PIPE=subprocess.PIPE
    proc = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=shell)
    cmd_stdout, cmd_stderr = proc.communicate()
    cmd_stdout = cmd_stdout.decode('utf-8')
    cmd_stderr = cmd_stderr.decode('utf-8')
    cmd_return = proc.returncode

    # ---
    # Note: Better to leave newlines in the stdout for debugging purposes
    # ---
    # Strip off the extra newline from the output if there is only one line of output
    # newlines_cnt = cmd_stdout.count('\n')
    # if newlines_cnt == 1:
    #     if DBG: pindent("DBG: Got only 1 line in stdout, removing newline for printing.")
    #     # todo: fix this problem: tcmd date "" is pass or fail depending on line below
    #     #       tcmd date "^$" because ^$ matches a newline for some reason
    #     # cmd_stdout = cmd_stdout.rstrip()
    # cmd_stdout = cmd_stdout.rstrip('\n')
    # cmd_stderr = cmd_stderr.rstrip('\n')
    # cmd_return = str(cmd_return).rstrip('\n')
    cmd_return = str(cmd_return)

    # ---
    # Indent multilines properly
    if DBG: pindent("DBG: cmd_return: [%s]" % cmd_return)
    if DBG: # pindent("DBG: cmd_stderr: [%s]" % cmd_stderr)
        if cmd_stderr.count('\n') == 1 or cmd_stderr.count('\n') == 0:
            pindent("DBG: cmd_stderr: [%s]" % cmd_stderr)
        else:
            pindent("DBG: cmd_stderr:")
            print (indent("["+cmd_stderr+"]", nspaces=11))
    if DBG: # pindent("DBG: cmd_stdout: [%s]" % cmd_stdout)
        if cmd_stdout.count('\n') == 1 or cmd_stdout.count('\n') == 0:
            pindent("DBG: cmd_stdout: [%s]" % cmd_stdout)
        else:
            pindent("DBG: cmd_stdout:")
            print (indent("["+cmd_stdout+"]", nspaces=11))
    if DBG: pindent("---")

    return (cmd_stdout, cmd_stderr, cmd_return)

def escape_regex(regex):
    """
    Escape regex metachars so user does not have to backslash them on command line

    :param regex: The regular expression to backslash metachars in

    :return: Properly backslashed regular expression metachars in regex
    """

    # src: https://stackoverflow.com/questions/4202538/escape-regex-special-characters-in-a-python-string
    regex = re.escape(regex)  ## This works better but regex is ugly in -v output
    # regex = re.sub(r'([\.\\\+\*\?\[\^\]\$\(\)\{\}\!\<\>\|\:\-])', r'\\\1', regex)

    return regex


def get_help_msg(command):
    """
    Print full help message of click def <function>

    Ex: print_help_msg(testcmd)

    :param command: function that has the click command decorator and help option
    :return: a string containting the @click.command() <function> help message
    """
    with click.Context(command) as ctx:
        # click.echo(command.get_help(ctx))
        return command.get_help(ctx)

# ---
# Define command line options and parameters
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
# @click.command(cls=CatchAllExceptions, context_settings=CONTEXT_SETTINGS, options_metavar='[options]')
@click.command(context_settings=CONTEXT_SETTINGS, options_metavar='[options]')
# @click.command()
@click.option('--dbg',         '-d', is_flag=True, default=False, help='Turn debug output on', metavar='<text>')
@click.option('--error',       '-e', is_flag=False,default='^$',  help='Stderr compared to regex', metavar='<text>')
@click.option('--negate',      '-n', is_flag=True, default=False, help='Opposite (negate) regex operator like grep -v', metavar='<text>')
@click.option('--comment',     '-c', is_flag=False,default=None,  help='Add a comment to Pass/Fail lines', metavar='<text>')
@click.option('--stdin',       '-s', is_flag=True, default=False, help='Pipe stdin as cmd subsitute with :', metavar='<text>')
@click.option('--return_code', '-r', is_flag=False,default='0',   help='The return status compared to regex', metavar='<text>')
@click.option('--verbose',     '-v', is_flag=True, default=False, help='Turn verbose output on', metavar='<text>')
@click.option('--pydoc',       '-p', is_flag=True, default=False, help='Generate pydoc')
@click.option('--timer',       '-t', is_flag=True, default=False, help='Report Execution time in seconds')
@click.option('--backslash',   '-b', is_flag=True, default=False, help='Backslash all regex meta chars')
@click.option('--min',         '-m', is_flag=True, default=False, help='Print only minimum one line Pass or Fail except if --dbg')
@click.help_option('--help',   '-h', help="This usage message")
@click.argument('cmd')
@click.argument('regex')


def testcmd(dbg, verbose, pydoc, cmd, regex, error, return_code, negate, stdin, comment, timer, backslash, min):
    """\b
tcmd - test a commands output against a regular expression

\b
 Desc: tcmd [Options] cmd regEx
         ====================================================================
         cmd      ........... cmd to execute and test stdout, stderr, exit status
         regEx    ........... regular expression to test the expected stdout of
                              the command
         ====================================================================
\b
Examples:
  tcmd date 2018          ... same as: date | grep -i 2018
\b
  tcmd -c "date test" date 2018
                          ... date | grep -i 2018 with a comment added to Pass/Fail lines
\b
  date | tcmd -s -c "cmd=date via --stdin" : 2018
                          ... same as line above only using stdin and not testing return_code and stderr
\b
  tcmd -n date 2016       ... date | grep -v 2016 (negate regEx test=Pass)
\b
  tcmd -d 'cat /etc/hosts' '#|localhost'
                          ... cat /etc/hosts | egrep -i "#|localhost"
\b
  tcmd -d -v date 2018    ... turn on debug and verbose output and check date cmd against regex 2018
\b
  tcmd -v "touch myfile; test -f myfile && rm -f myfile"  ""
                          ... sting multiple commands together with ';' or && or ||
\b
  OUT=$(cat /etc/hosts)
  echo "$OUT" | tcmd --stdin -v -c "bash variable test" : localhost
                          ... echo "$OUT" | grep -i localhost (uses a bash variable w/--stdin)
\b
  OUT=$(tcmd ping -c 2 localhost); RET=$?
  if [ $RET -eq 0 ] && echo "tcmd returned 0" || echo "tcmd did not return 0"
                          ... how to run tcmd and capturing just PASS (0) or FAil (1) return code without
                          ... printing tcmd output to stdout
\b
  tcmd -h                 ... this help message
\b
Notes:
\b
  1. You can specify regEx as "", "^$", or "\A\z" for the empty string
  2. regex matches re.MULTILINE and re.DOTALL (matches across multilines with ".")
  3. This program only tested on python 2.7
  4. This program requires textwrap and click python modules to be installed
     Run: 'pip install -r inc/requirements.txt' to install these two modules
  5. See tests/test_tcmd.sh for more examples of syntax
\b
Warning:
  1. You have to backslash regular expression meta chars on command line if you want them
     to be interpreted as literal characters in the regex
     (tcmd does not escape the metachars for you unless you use the --backslash option)
     For example, use:
       tcmd -v 'echo "add x+y"' "add x\+y"
                                     (^ backslashed the '+' regex metachar)
         instead of
       tcmd -v 'echo "add x+y"' "add x+y"
     Python regex metachars:
       \       Escape special char or start a sequence.
       .       Match any char except newline, see re.DOTALL
       ^       Match start of the string, see re.MULTILINE
       $       Match end of the string, see re.MULTILINE
       []      Enclose a set of matchable chars
       R|S     Match either regex R or regex S.
       ()      Create capture group, & indicate precedence
       *       0 or more. Same as {,}
       +       1 or more. Same as {1,}
       ?       0 or 1. Same as {,1}
"""
    global DBG

    if dbg: DBG=1
    if DBG: pindent("DBG: len(sys.argv): %s" % len(sys.argv))

    if timer:
        start_time = datetime.now()
        if DBG: pindent("Start_time: %s" % start_time)

    # ---
    # Escape the regex metachars so people do not have backslash them on command line
    if backslash:
        # src: https://stackoverflow.com/questions/4202538/escape-regex-special-characters-in-a-python-string
        # regex = re.escape(regex)  ## This works better but regex is ugly in -v output
        # Fails: regex = re.sub(r'([\.\\\+\*\?\[\^\]\$\(\)\{\}\!\<\>\|\:\-])', r'\1', regex)
        regex = escape_regex(regex)

    # ---
    # Generate pydoc if given on command line
    if pydoc:
        create_pydocs()
        exit(0)

    # ---
    # Set defaults for options -e and -r
    stderr_regex      = str(error)
    return_code_regex = str(return_code)

    # ---
    # Make sure we have cmd and regex from cmd line args
    if len(sys.argv) <= 2: # first arg is always the name of the program, fyi, need at least 3 here
        click.echo(get_help_msg(testcmd))
        exit(1)

    # ---
    # Get the command that is being run for debug and verbose reporting
    cmd_str = ""
    if [ 'tcmd' in sys.argv[0] ]:
        cmd_str += "tcmd "
    cmd_str += ' '.join(sys.argv[1:])

    # ---
    # Print some debugging info on the cmd line options
    if DBG: pindent("DBG:       regex: [%s]" % regex)
    if DBG: pindent("DBG:         cmd: [%s]" % cmd)
    if DBG: pindent("---")
    if DBG:
        pindent("DBG:       error: [%s]" % error)
        pindent("DBG: return_code: [%s]" % return_code)
        pindent("DBG:     verbose: [%s]" % verbose)
        pindent("DBG:         dbg: [%s]" % dbg)
        pindent("DBG:      negate: [%s]" % negate)
        pindent("DBG:       stdin: [%s]" % stdin)
        pindent("DBG:       pydoc: [%s]" % pydoc)
        pindent("DBG:     comment: [%s]" % comment)
        pindent("DBG:       timer: [%s]" % timer)
        pindent("DBG:         min: [%s]" % min)
        pindent("DBG:   backslash: [%s]" % backslash)
        pindent("---")

    # ---
    # Run the command
    if stdin:
        # Overwrite stdout with stdin pipe
        cmd_stdout, cmd_stderr, cmd_return = _runcmd(cmd)
        cmd_stdout_list = sys.stdin.readlines()
        cmd_stdout = "".join(cmd_stdout_list)
        cmd_stdout = cmd_stdout.rstrip('\n')
        cmd = "<stdin> " + cmd
        print("a")
        if DBG: pindent("DBG: stdin->cmd_stdout: [%s]" % cmd_stdout)
    else:
        cmd_stdout, cmd_stderr, cmd_return = _runcmd(cmd)
        # New python 3 problem conversions
        # cmd_stdout = cmd_stdout.decode('utf-8')
        # cmd_stderr = cmd_stderr.decode('utf-8')

    # ---
    # Must set regex to empty string explicitly because tcmd date "" prints "Pass:"
    # if not regex or regex == '^$':
    #     src: https://stackoverflow.com/questions/19127384/what-is-a-regex-to-match-only-an-empty-string
    #     regex = r'^$' # matches empty string AND newline
    #     regex = '\A\z'
    #     regex = '^$'
    #     regex = '^$'; # this is matching a newline somehow (removing the newline makes it pass)

    def isBlank (myString):
        """
        Check if myString is an empty string without using regular expressions
        Src: https://stackoverflow.com/questions/9573244/most-elegant-way-to-check-if-the-string-is-empty-in-python

        :param myString: cmd_stdout string to check if empty
        :return:         True or False
        """
        if myString and myString.strip():
            # myString is not None AND myString is not empty or blank
            return False
        # myString is None OR myString is empty or blank
        return True

    # ---
    # Now check cmd_stdout against the regex and print Pass or Fail
    # Src: https://www.thegeekstuff.com/2014/07/advanced-python-regex/ ## DOTALL allows "." across '\n' boundries
    ##stdout_searchObj      = re.search(            regex, cmd_stdout, re.DOTALL|re.MULTILINE|re.IGNORECASE)
    # ---
    # Note: Have to special case empty strings because of python re matching ^$ problem
    # Note: regex is false when: tcmd date ""
    # Note: To get around using a regex I use
    # stdout_searchObj = False
    if not regex or regex == '^$' or regex == '\A\z': # Expecting an empty cmd_stdout
        if isBlank(cmd_stdout):
            stdout_searchObj = True
        else:
            stdout_searchObj = False
    else:
        stdout_searchObj  = re.search(regex, cmd_stdout, re.DOTALL|re.MULTILINE|re.IGNORECASE)

    # ---
    # Have to do the same thing for stderr_regex for tcmd -n -d -v -r 127 -e "" dat "" to Pass
    if not stderr_regex or stderr_regex == '^$' or stderr_regex == '\A\z': # Expecting an empty cmd_stdout
        if isBlank(cmd_stderr):
            stderr_searchObj = True
        else:
            stderr_searchObj = False
    else:
        stderr_searchObj  = re.search(stderr_regex,      cmd_stderr, re.DOTALL|re.MULTILINE|re.IGNORECASE)
    return_code_searchObj = re.search(return_code_regex, cmd_return, re.DOTALL|re.MULTILINE|re.IGNORECASE)

    # ---
    # Print the types of the search (boolean or regex.search)
    if DBG: pindent("DBG: type(stdout_searchObj):      %s" % type(stdout_searchObj))
    if DBG: pindent("DBG: type(stderr_searchObj):      %s" % type(stderr_searchObj))
    if DBG: pindent("DBG: type(return_code_searchObj): %s" % type(return_code_searchObj))

    # ---
    # Print out stdout regex test search result
    if DBG and not isinstance(stdout_searchObj, bool) and stdout_searchObj:
        pindent("DBG:      stdout_searchObj : [%s]" % stdout_searchObj.group())
    elif DBG and isinstance(stdout_searchObj, bool):
        pindent("DBG:      stdout_searchObj : [%s] (boolean)" % stdout_searchObj)

    # ---
    # Print out stderr regex test search result
    if DBG and not isinstance(stderr_searchObj, bool) and stderr_searchObj:
        pindent("DBG:      stderr_searchObj : [%s]" % stderr_searchObj.group())
    elif DBG and isinstance(stderr_searchObj, bool):
        pindent("DBG:      stderr_searchObj : [%s] (boolean)" % stderr_searchObj)

    # if DBG and stderr_searchObj:      pindent("DBG:      stderr_searchObj : [%s]" % stderr_searchObj.group())

    # ---
    # Print out return_code result
    if DBG and return_code_searchObj: pindent("DBG: return_code_searchObj : [%s]" % return_code_searchObj.group())
    if DBG: pindent("---")

    # ---
    # Change the stdout_searchObj to the opposite boolean of the actual for --negate option
    if negate:
        stdout_searchObj = not stdout_searchObj
        regex = "<negate> "+regex
        if DBG: pindent("DBG: stdout_searchObj: %s" % stdout_searchObj)

    # ---
    # Indent multiline stdout lines so Pass and Fail are easily visible
    # multiline_stdout = re.search( "\n.*\n", cmd_stdout, re.M|re.I)
    # if multiline_stdout:
    #     cmd_stdout = re.sub( '^',' '*6, cmd_stdout , flags=re.MULTILINE )
    #     cmd_stdout = cmd_stdout.lstrip()

    if timer and not min:
        now = datetime.now()
        elapsed_time = now - start_time

    if comment:
        add_comment = " # "+comment
    else:
        add_comment = ""

    def print_verbose():
        """ Prints out detailed info on actual vs expected for stdout, stderr, and return value"""
        pindent("")
        pindent("          cmd: [%s]" % cmd_str)
        pindent("")
        pindent("actual_return: [%s] expect_return: [%s]"  % (cmd_return, return_code_regex))
        pindent("actual_stderr: [%s]  expect_stderr: [%s]" % (cmd_stderr, stderr_regex))
        # print ("dbg: cmd_stderr: ", type(cmd_stderr))
        if cmd_stderr.count('\n') == 1 or cmd_stderr.count('\n') == 0:
            pindent("actual_stderr: [%s]  expect_stderr: [%s]" % (cmd_stderr, stderr_regex))
        else:
            pindent("")
            pindent("expect_stderr: [%s]" % stderr_regex)
            pindent("actual_stderr: ")
            print (indent("["+cmd_stderr+"]", nspaces=10))
        pindent("")
        pindent("expect_stdout: [%s]" % regex)
        if cmd_stdout.count('\n') == 1 or cmd_stdout.count('\n') == 0:
            pindent("actual_stdout: [%s]" % cmd_stdout)
        else:
            pindent("actual_stdout: ")
            print (indent("["+cmd_stdout+"]", nspaces=10))

    # ---
    # Test passes if all 3 regex matched
    if stdout_searchObj and stderr_searchObj and return_code_searchObj:

        click.echo("Pass: cmd [%s]; regex [%s]" % (cmd, regex)+add_comment)

        if not min:
            if verbose:
                print_verbose()
            if timer:
                pindent("---")
                pindent("Elapsed Time: %s" % elapsed_time)
        exit(0)

    else:
        # ---
        # Test Fails
        # Set verbose=True so that details of failure are printed for debugging
        verbose=True

        # ---
        # Print out the first searchObj that failed starting with stdout vs regex
        if not stdout_searchObj:
            click.echo("Fail: cmd [%s] stdout does *NOT* match regEx [%s]" % (cmd, regex)+add_comment)
        elif not stderr_searchObj:
            click.echo("Fail: cmd [%s] stderr does *NOT* match regEx [%s]" % (cmd, stderr_regex)+add_comment)
        elif not return_code_searchObj:
            click.echo("Fail: cmd [%s] return code does *NOT* match regEx [%s]" % (cmd, return_code_regex)+add_comment)
        else:
            click.echo("Fail: cmd [%s] did *NOT* match for some reason" % (cmd)+add_comment)

        if not min:
            if verbose:
                print_verbose()
            if timer:
                pindent("---")
                pindent("Elapsed Time: %s" % elapsed_time)
        exit(1)


if __name__ == '__main__':
    try:
        testcmd()
    except (Exception):
    # except (Exception, err):
        # click.echo("Fail: There was an error during execution of tcmd:")
        print("Fail: There was an error during execution of tcmd:")
        exc_type, exc_value, exc_tb = sys.exc_info()
        for line in traceback.format_exception(exc_type, exc_value, exc_tb):
            pindent(line)
        exit(1)

