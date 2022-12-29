import argparse
import sys

def read_file(filename):
    with open(filename) as file:
        return file.readlines()

def url_parser(url):
    
    parts = urlparse(url)
    directories = parts.path.strip('/').split('/')
    queries = parts.query.strip('&').split('&')
    
    elements = {
        'scheme': parts.scheme,
        'netloc': parts.netloc,
        'path': parts.path,
        'params': parts.params,
        'query': parts.query,
        'fragment': parts.fragment,
        'directories': directories,
        'queries': queries,
    }
    return elements

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', default='input.txt', help='input.txt')
    args = parser.parse_args()
    print(args)
    try:
        url = read_file(filename)
        parsed = url_parser(url)
        print(parsed)
    except:
        sys.exit(err)    