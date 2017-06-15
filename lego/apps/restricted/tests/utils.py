def read_file(filename):
    """Read a file, used to load email fixtures"""
    with open(filename, 'r') as file:
        return file.read()
