import os

def get_directory():
    path = ""
    path = '/Users/benhoskings/Documents/Projects/hero-monitor'
    if os.path.isdir(path):
        return path
    elif os.path.isdir():
        return None
