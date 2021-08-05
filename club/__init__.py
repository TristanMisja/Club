#!/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum
import subprocess
import termios
import fnmatch
import pathlib
import struct
import random
import fcntl
import tty
import sys
import os
import gc
import io

__authors__ = ("Tristan S. Misja")
__version__ = "1.0.0"
__license__ = "MIT"
__copyright__ = "Copyright © 2021 Tristan S. Misja"
__credits__ = []
__maintainer__ = "Tristan S. Misja"
__email__ = "TristanMisja09@gmail.com"
__status__ = "Release"
__doc__ = None

class CommandlineError(OSError):
    pass


def quit(message=''):
    """
    Quits the program by killing the current
    running process.
    
    It will leave any child processes/threads
    running.
    """
    if message:
        sys.stderr.write(message)
        sys.stderr.flush()
    os.kill(os.getpid(), 9)


def safe_quit(message=''):
    """
    Quits the program by killing the current
    running process.
    
    It will also kill any child processes/threads.
    """
    if message:
        sys.stderr.write(message)
        sys.stderr.flush()

    childpidlist = []
    out = str(subprocess.check_output(['sudo','ps','--ppid',str(os.getpid())],stdin=subprocess.PIPE,stderr=subprocess.PIPE))
    out = '\n'.split(out)
    out.pop(0)
    for cpidinfo in out:
        childpidlist.append(int(cpidinfo.split('/')[1].split(' ')[0]))

    for cpid in childpidlist:
        os.kill(cpid, 9)

    os.kill(os.getpid(), 9)


def print_error(error):
    """
    Writes error argument to stderr.
    """
    sys.stderr.write(str(error))
    sys.stderr.flush()


def get_fp_from_fd(fd):
    """
    Takes a fd and then returns the file that the fd came from.
    """
    return os.readlink(f"/proc/{os.getpid()}/fd/{fd.fileno()}")


def getch():
    """
    Returns keycode when a key is pressed.
    """
    fd = sys.stdin.fileno()
    
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ord(ch)


# def getchar():
#     """
#     Returns key when one is pressed.
#    """
#     keycode = getch()
# 
#     special = {
#         127: 'backspace',
#         32: 'space',
#         9: 'tab',
#         27: 'esc',
#         65: 'arrow_up',
#         66: 'arrow_down',
#         67: 'arrow_right',
#         68: 'arrow_left',
#         13: 'enter',
#         20: 'caps_lock',
#         17: 'ctrl',
#         16: 'shift'
#     }
# 
#     if keycode in special.keys():
#         ch = special[keycode]
#     else:
#         ch = chr(keycode)
#
#     return ch


def getpass(prompt: str = "Password: ", mask: str = ''):
    """
    An improved version of getpass.getpass
    """
    if len(mask) not in [1,0]:
        raise ValueError("Mask can only be 1 digit long!")

    if mask == '' or sys.stdin != sys.__stdin__:
        return getpass.getpass(prompt)
    else:
        enteredpassword = []
        sys.stdout.write(prompt)
        sys.stdout.flush()
        while 1:
            key = ord(getch())
            if key == 13:
                sys.stdout.write('\n')
                return ''.join(enteredpassword)
            elif key in [8, 127]:
                if len(enteredpassword) > 0:
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                    enteredpassword = enteredpassword[:-1]
                elif 0 <= key <= 31:
                    continue
                else:
                    char = chr(key)
                    sys.stdout.write(mask)
                    sys.stdout.flush()
                    enteredpassword.append(char)


class Foreground(Enum):
    RED = '\33[31m'
    BRIGHT_RED = '\33[91m'
    GREEN = '\33[32m'
    BRIGHT_GREEN = '\33[92m'
    YELLOW = '\33[33m'
    BRIGHT_YELLOW = '\33[93m'
    BLUE = '\33[34m'
    BRIGHT_BLUE = '\33[94m'
    PURPLE = '\33[35m'
    BRIGHT_PURPLE = '\33[95m'
    VIOLET = '\33[35m'
    BRIGHT_VOILET = '\33[95m'
    CYAN = '\x1b[6;30;36m'
    BRIGHT_CYAN = '\x1b[6;30;96m'
    BLACK = '\33[30m'
    GRAY = '\33[90m'
    GREY = '\33[90m'
    WHITE = '\33[97m'
    RESET = '\33[0m'


class Background(Enum):
    RED = '\33[41m'
    BRIGHT_RED = '\33[101m'
    GREEN = '\33[42m'
    BRIGHT_GREEN = '\33[102m'
    YELLOW = '\33[43m'
    BRIGHT_YELLOW = '\33[103m'
    BLUE = '\33[44m'
    BRIGHT_BLUE = '\33[104m'
    PURPLE = '\33[45m'
    BRIGHT_PURPLE = '\33[105m'
    VIOLET = '\33[45m'
    BRIGHT_VOILET = '\33[105m'
    CYAN = '\x1b[6;30;46m'
    BRIGHT_CYAN = '\x1b[6;30;106m'
    BLACK = '\33[40m'
    GRAY = '\33[100m'
    GREY = '\33[100m'
    WHITE = '\33[47m'
    RESET = '\33[0m'


class Effects():
    ITALIC = '\33[3m'
    BLINK = '\33[5m\33[6m'
    UNDERLINE = '\x1b[4m'
    OVERLINE = '\x1b[53m'
    NEGATIVE = '\33[7m'
    ERROR = '\33[5m\33[6m\33[91m'
    BOLD = '\x1b[1m'
    FAINT = '\x1b[2m'
    CROSS = '\x1b[9m'
    RESET = '\33[0m'


def cls():
    """
    Clears the console.
    """
    for _ in range(os.get_terimal_size().rows):
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')
    sys.stdout.flush()


def clearlines(lines=1):
    """
    Clears the amount of lines specified.
    """
    for _ in range(lines):
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')
        sys.stdout.flush()


def fancyprint(*args, sep: str = ' ', start: str = '', end: str = '\n', fore: str = '', back: str = '', color: str = '\33[0m', case: str = 'normal', file=sys.stdout, **kwargs):
    """
    An very improved version of print().
    
    Works the same, but you can change the case, color, and more.
    """
    args2 = []
    case = case.lower()
    
    try:
        file.write('')
    except TypeError:
        try:
            file.write(b'')
        except io.UnsupportedOperation:
            file = open(os.readlink('/proc/' + str(os.getpid()) + '/fd/' + str(fd.fileno())),'w')
    except io.UnsupportedOperation:
        file = open(os.readlink('/proc/' + str(os.getpid()) + '/fd/' + str(fd.fileno())),'w')
    
    if fore == '' or back == '':
        if fore == '':
            fore = color
        if back == '':
            back = color
        color = ''
    
    for arg in args:
        arg = arg.split(' ')
        for argument in arg:
            args2.append(argument)
    
    if case in ['camel','camelcase','lowercamel','lowercamelcase','camel-case','lowercamel-case','lower-camelcase','lower-camel-case','lower-camel']:
        joinlist = [args2[0][0].lower() + args2[0][1::]]
        args2.pop(0)
        for string in args2:
            string = string.replace(',','').replace('-','').replace('\'','').replace('\"','').replace('<','').replace('>','').replace('_','').replace('!','').replace('?','').replace('$','').replace('%','').replace('@','').replace('^','').replace('&','').replace('*','').replace('`','').replace('~','').replace('\\','').replace('/','').replace('{','').replace('}','').replace('[','').replace(']','').replace(':','').replace(';','').replace('+','').replace('=','')
            joinlist.append(string[0].upper() + string[1::])
                
        text = str(color + fore + back + start + ''.join(joinlist) + end + '\33[0m')
    
    elif case in ['train','traincase','train-case']:
        joinlist = [args[0][0].upper() + args2[0][1::]]
        for string in args2:
            if string == args2[0]:
                continue
            else:
                joinlist.append(string.lower())
        text = str(color + fore + back + start + '-'.join(joinlist) + end + '\33[0m')
    
    elif case in ['sentence','sentencecase','sentence-case']:
        joinlist = [args[0][0].upper() + args2[0][1::]]
        for string in args2:
            if string == args2[0]:
                continue
            else:
                joinlist.append(string)
        text = str(color + fore + back + start + ' '.join(joinlist) + end + '\33[0m')
    
    elif case in ['leet','leetcase','leet-case']:
        joinlist = []
        for string in args2:
            joinlist.append(string.replace('e','3').replace('E','3').replace('i','1').replace('I','1').replace('s','5').replace('S','5').replace('z','2').replace('Z','2').replace('a','4').replace('A','4').replace('b','8').replace('B','8').replace('o','0').replace('O','0'))
        text = str(color + fore + back + start + sep.join(joinlist) + end + '\33[0m')
    
    elif case in ['pascal','pascalcase','pascal-case','capitalcamel','capital-camel','capitalcamel-case','capital-camelcase','capital-camel-case','capitalcamelcase']:
        joinlist = []
        for string in args2:
            joinlist.append(string[0].upper() + string[1::])
        text = str(color + fore + back + start + ''.join(joinlist) + end + '\33[0m')
    
    elif case in ['snake','snakecase','snake-case','snake_case','c','ccase','c-case','c_case']:
        joinlist = []
        for arg in args2:
            joinlist.append(arg.lower())
        text = str(color + fore + back + start + '_'.join(joinlist) + end + '\33[0m')
    
    elif case in ['flat','flatcase','flat-case']:
        joinlist = []
        for arg in args2:
            joinlist.append(arg.lower())
        text = str(color + fore + back + start + ''.join(joinlist) + end + '\33[0m')
    
    elif case in ['spinal','spinalcase','spinal-case','hyphen','hyphencase','hyphen-case','dash','dashcase','dash-case']:
        joinlist = []
        for arg in args2:
            joinlist.append()
        text = str(color + fore + back + start + '-'.join(joinlist) + end + '\33[0m')
    
    elif case in ['macro','macrocase','macro-case']:
        joinlist = []
        for arg in args2:
            joinlist.append(arg.upper())
        text = str(color + fore + back + start + '_'.join(joinlist) + end + '\33[0m')
    
    elif case in ['cobol','cobolcase','cobol-case']:
        joinlist = []
        for arg in args2:
            joinlist.append(arg.upper())
        text = str(color + fore + back + start + '-'.join(joinlist) + end + '\33[0m')
    
    elif case in ['kebab','kebabcase','kebab-case','lisp','lispcase','lisp-case','css','csscase','css-case']:
        joinlist = []
        for arg in args2:
            joinlist.append(arg.lower())
        text = str(color + fore + back + start + '-'.join(joinlist) + end + '\33[0m')
    
    elif case in ['upper','uppercase','upper-case']:
        joinlist = []
        for string in args2:
            joinlist.append(string.upper())
        text = str(color + fore + back + start + sep.join(joinlist) + end + '\33[0m')
    
    elif case in ['lower','lowercase','lower-case']:
        joinlist = []
        for string in args2:
            joinlist.append(string.lower())
        text = str(color + fore + back + start + sep.join(joinlist) + end + '\33[0m')
    
    elif case in ['random','randomcase','random-case']:
        joinlist = []
        for string in args2:
            secondjoinlist = []
            for char in string:
                char = random.choice([char.upper(),char.lower()])
                secondjoinlist.append(char)
            temp = ''.join(secondjoinlist)
            joinlist.append(temp)
        text = str(color + fore + back + start + sep.join(args2) + end + '\33[0m')
    
    elif case in ['sticky','stickycase','sticky-case','studly','studlycase','studly-case']:
        joinlist = []
        for string in args2:
            secondjoinlist = []
            for char in string:
                if char.isupper():
                    secondjoinlist.append(char.lower())
                elif char.islower():
                    secondjoinlist.append(char.upper())
                else:
                    secondjoinlist.append(char)
            joinlist.append(''.join(secondjoinlist))
        text = str(color + fore + back + start + sep.join(joinlist) + end + '\33[0m')
    
    else:
        joinlist = []
        for word in args2:
            joinlist.append(''.join(word))
        text = str(color + fore + back + start + sep.join(joinlist) + end + '\33[0m')
    
    file.write(color + start + text + end + '\33[0m')
    file.flush()

    cleanmemory()

    return text

def cleanmemory():
    sys.stdout.flush()
    sys.__stdout__.flush()
    sys.stdin.flush()
    sys.__stdin__.flush()
    sys.stderr.flush()
    sys.__stderr__.flush()

    gc.unfreeze()
    for obj in gc.get_objects(generation=None):
        del obj

    gc.collect(2)
    gc.collect(1)
    gc.collect(0)


def quit(message=None):
    """
    Used to exit the program.
    """
    if message in [None,'null',0]:
        raise SystemExit
    else:
        raise SystemExit(str(message))


def typer(text, delay=0.08, out=sys.stdout):
    """
    Like print(), but looks like someone is typing.
    
    The delay argument is the amount of
    seconds between characters, and out is
    the stream to send the characters
    to (stdout by default)
    """
    for char in text:
        out.write(char)
        out.flush()
        time.sleep(delay)


def center_text(text):
    """
    Adds spaces to make a string
    be centered in the terminal.
    """
    space_count = (os.get_terminal_size().columns / 2) - (len(str(text)) / 2)
    spaces = (' ' * space_count)
    return spaces + str(text)


def Stack(object):
    """
    A basic stack object.
    """
    def __init__(self, start=[]):
        self.stack = []
        for x in stack:
            self.push(x)
        self.reverse()
        
    def push(self, obj):
        self.stack = [obj] + self.stack
        
    def pop(self):
        if not self.stack:
            raise Exception("Underflow while attempting to pop stack!")
        top, *self.stack = self.stack
        return top
    
    def top(self):
        if not self.stack:
            raise Exception("Underflow while attempting to get top of stack!")
        return self.stack[0]
    
    def empty(self):
        return not self.stack
    
    def __repr__(self):
        return f'<Stack {repr(self.stack)}>'
    
    def __str__(self):
        return str(self.stack)
    
    def __eq__(self, other):
        return self.stack == other.stack
        
    def __len__(self):
        return len(self.stack)
    
    def __add__(self, other):
        return Stack(self.stack + other.stack)
    
    def __mul__(self, reps):
        return Stack(self.stack * reps)
    
    def __getitem__(self, offset):
        return self.stack[offset]
    
    def __getattr__(self, name):
        return getattr(self.stack, name)
    
    def __new__(cls):
        return object.__new__(cls)
    
    def __iadd__(self, other):
        return Stack(self.stack + other.stack)
    
    def __imul__(self, reps):
        return Stack(self.stack * reps)
    
    def __unicode__(self):
        return str(self.stack).encode('utf8')
    
    def __sizeof__(self):
        return sys.getsizeof(self.stack)


class Set(object):
    def __init__(self, value=[]):
        self.data = {}
        self.concat(value)
        
    def intersect(self, other):
        res = {}
        for x in other:
            if x in self.data:
                res[x] = None
        return Set(res.keys)
    
    def union(self, other):
        res = {}
        for x in other:
            res[x] = None
        for x in self.data.keys():
            res[x] = None
        return Set(res.keys())
    
    def concat(self, value):
        for x in value:
            self.data[x] = None
                
    def __len__(self):
        return len(self.data.keys())
    
    def __new__(cls):
        return object.__new__(cls)
    
    def __getitem__(self, ix):
        return list(self.data.keys())[ix]
     
    def __and__(self, other):
        return self.intersect(other)
    
    def __or__(self, other):
        return self.union(other)
    
    def __repr__(self):
        data = str(list(self.data.keys()))
        data[0] = '{'
        data[len(data)] = '}'
        return f'<Set {data}>'
    
    def __str__(self):
        data = str(list(self.data.keys()))
        data[0] = '{'
        data[len(data)] = '}'
        return data
    
    def __eq__(self, other):
        return self.data == other.data


class BinaryTree(object):
    def __init__(self):
        self.tree = EmptyNode()
    
    def __repr__(self):
        return f'<BinaryTree {repr(self.tree)}>'
    
    def lookup(self, value):
        return self.tree.lookup(value)
    
    def insert(self, value):
        self.tree = self.tree.insert(value)


class EmptyNode(object):
    """
    A placeholder for BinaryNode()
    """
    def __repr__(self):
        return '*'
    
    def lookup(self, value):
        return False
    
    def insert(self, value):
        return BinaryNode(self, value, self)


class BinaryNode(object):
    """
    A binary node object.
    """
    def __init__(self, left, value, right):
        self.data, self.left, self.right = value, left, right
        
    def lookup(self, value):
        if self.data == value:
            return True
        elif self.data > value:
            return self.left.lookup(value)
        else:
            return self.right.lookup(value)
        
    def insert(self, value):
        if self.data > value:
            self.left = self.left.insert(value)
        elif self.data < value:
            self.right = self.right.insert(value)
        return self
    
    def __repr__(self):
        return f'<BinaryNode {self.left} {self.data} {self.right}>'


def KeyedBinaryTree(object):
    def __init__(self):
        self.tree = KeyedEmptyNode()
        
    def __repr__(self):
        return f'<KeyedBinaryTree {repr(self.tree)}>'
    
    def lookup(self, key):
        return self.tree.lookup(key)
    
    def insert(self, key, value):
        self.tree = self.tree.insert(key,value)


class KeyedEmptyNode(object):
    """
    A placeholder for KeyedBinaryNode()
    """
    def __repr__(self):
        return '*'
    
    def lookup(self, value):
        return None
    
    def insert(self, key, value):
        return KeyedBinaryNode(self, key, value, self)


class KeyedBinaryNode(object):
    def __init__(self, left, value, right):
        self.val, self.key, self.left, self.right = value, key, left, right
        
    def lookup(self, key):
        if self.key == key:
            return self.val
        elif self.key > key:
            return self.left.lookup(key)
        else:
            return self.right.lookup(key)
        
    def insert(self, key, value):
        if self.key == key:
            self.val = value
        elif self.key > key:
            self.left = self.left.insert(key, value)
        elif self.key > key:
            self.right = self.right.insert(key, value)
        return self
    
    def __repr__(self):
        return f'<KeyedBinaryNode {self.left} {self.key} {self.data} {self.right}>'


class Graph(object):
    """
    An object for graph searching
    """
    def __init__(self, label, extra):
        self.name = label
        self.data = extra
        self.arcs = []
        
    def __repr__(self):
        return self.name
    
    def search(self, goal):
        Graph.solns = []
        self.generate([self], goal)
        Graph.solns.sort(key=lambda x: len(x))
        return Graph.solns
    
    def generate(self, path, goal):
        if self == goal:
            Graph.solns.append(path)
        else:
            for arc in self.arcs:
                if arc not in path:
                    arc.generate(path + [arc], goal)


class ArgumentParser(object):
    """
    An alternative to argparse.ArgumentParser
    and optparse.OptionParser.
    
     args - Expected to be sys.argv
    """
    def __init__(self, args):
        if type(args) in [tuple, list]:
            self.args = list(args)
        elif type(args) == str:
            self.args = args.split(' ')
        self.arguments = []
        self.options = []
        self.help = []
        
    def add_argument(self, names: list, dest):
        self.arguments.append([names, dest])
        
    def add_option(self, names: list, dest, type_=str, defaultval=None, required=False):
        self.options.append([names, dest, type_, defaultval, required])
        
    def add_help(self, help_string, accept_dash_h=True, stdout=sys.stdout):
        self.help = [help_string, accept_dash_h, stdout]
        
    def parse_args(self):
        out = {"opts": {}, "args": []}
        
        for opt in self.options:
            for name in opt[0]:
                if name in self.args:
                    option = opt[2](sys.argv[sys.argv.index(name)+1])
                    out["opts"][opt[1]] = options
                elif '=' in name:
                    tmp = name.split('=')
                    if tmp[2] in self.args:
                        out["opts"][opt[1]] = opt[3]
                else:
                    if opt[4] == True:
                        out["opts"][opt[1]] = opt[3]
                        
        for arg in self.arguments:
            for name in arg[0]:
                if name in self.args:
                    out["args"].append(arg[1])
                
        if self.help == []:
            pass
        else:
            if self.help[1]:
                if '-h' in self.args or '--help' in self.args:
                    self.help[2].write(self.help[0])
                    self.help[2].flush()
                    sys.exit()
            else:
                if '--help' in self.args:
                    self.help[2].write(self.help[0])
                    self.help[2].flush()
                    sys.exit()


def encode_str(string):
    if type(string) == str:
        return string.encode(sys.getfilesystemencoding())
    elif type(string) == bytes:
        return string.decode().encode(sys.getfilesystemencoding())
    else:
        return str(string).encode(sys.getfilesystemencoding())


class DevNull(object):
    def __init__(self):
        if sys.platform in ['dos','win16']:
            self.nullfp = r'C:\DEV\NUL'
        elif sys.platform in ['win32','win64']:
            self.nullfp = r'C:\\Device\Null'
        else:
            self.nullfp = '/dev/null'
    
    def write(self,data):
        if type(data) == str:
            with open(self.nullfp,'w') as fd:
                fd.write(data)
        else:
            with open(self.nullfp,'wb') as fd:
                fd.write(data)
                
    def read(self,bytenum):
        return ''
    
    def readlines(self,linenums):
        return ['']
    
    def fileno(self):
        return open(self.nullfp,'rb').fileno()
    
    def close(self):
        pass
    
    def __str__(self):
        return self.nullfp
    
    def __repr__(self):
        return "<DevNull>"
    
    def flush(self):
        with open(self.nullfp,'w') as fd:
            fd.flush()


def glob(root, pattern):
    """
    Works just like glob.glob()
    """
    if root is None:
        return
    
    if os.path.isfile(root) and fnmatch.fnmatch(root, pattern):
        yield root
        return
    
    for base, dirs, files in os.walk(root):
        matches = fnmatch.filter(files, pattern)
        for filename in matches:
            yield os.path.join(base, filename)


def execute(cmd, verbose=False):
    """
    Executes shell command.
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = []
    while 1:
        line = p.stdout.readline()
        out.append(line)
        if verbose:
            print(line)
        if not line and p.poll() is not None:
            break
    if p.returncode != 0:
        print(p.stderr.read().strip())
        return 1
    else:
        return ''.join(out).strip()


# def daemonize():
#     """
#     Daemonizes the current process.
#     """
#     if os.fork():
#         os._exit(0)
#     os.chdir('/')
#     os.umask(22)
#     os.setsid()
#     os.umask(0)
#     if os.fork():
#         os._exit(0)
#     stdin = open(os.devnull)
#     stdout = open(os.devnull, 'w')
#     os.dup2(stdin.fileno(), 0)
#     os.dup2(stdout.fileno(), 1)
#     os.dup2(stdout.fileno(), 2)
#     stdin.close()
#     stdout.close()
#     os.umask(22)
#     for fd in range(3, 1024):
#         try:
#             os.close(fd)
#         except OSError:
#             pass
#     return os.getpid()


class Logger(object):
    """
    Used as a simpler logging object.
    """
    def __init__(self, file=sys.stdout):
        self.file = file
        self.logged_text = ''
        self.format = ''
    
    def config(self, **kwargs):
        if 'file' in kwargs:
            self.file = kwargs['file']
        if 'format' in kwargs:
            self.format = kwargs['format']
    
    def _parse_format(self):
        formatted = self.format
        if '{asctime}' in self.format:
            formatted = formatted.replace('{asctime}',time.ctime())
        if '{utime}' in self.format:
            formatted = formatted.replace('{utime}',str(time.time()))
        if '{line}' in self.format:
            formatted = formatted.replace('{line}',str(len(self.logged_text.split('\n')) + 1))
        return formatted
            
    def close(self):
        if not self.file == sys.stdout:
            self.file.close()
        else:
            self.file.flush()
        return logged_text
    
    def log(self, text):
        log = _parse_format(self):
        log += str(text)
        self.file.write(log)
        self.file.flush()
        self.logged_text += log
        self.logged_text += '\n'
        return log
    
    def get_log_history(self):
        return self.logged_text
