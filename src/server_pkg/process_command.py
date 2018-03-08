import subprocess

def process_command(pack):
    if pack.data == 'ls':
        print('\nFiles in current directory:\n', subprocess.getoutput('ls'))