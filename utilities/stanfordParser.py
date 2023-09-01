import os
from nltk.tree import *
from six.moves import urllib
import zipfile
import sys
import time

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Download zip file from https://nlp.stanford.edu/software/stanford-parser-full-2018-10-17.zip and extract in stanford-parser-full-2015-04-20 folder in higher directory
os.environ['CLASSPATH'] = os.path.join(BASE_DIR, 'stanford-parser')
os.environ['STANFORD_MODELS'] = os.path.join(BASE_DIR,'stanford-parser/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
os.environ['NLTK_DATA'] = '/usr/local/share/nltk_data/'

# checks if jar file of stanford parser is present or not
def is_parser_jar_file_present():
    stanford_parser_zip_file_path = os.environ.get('CLASSPATH') + ".jar"
    return os.path.exists(stanford_parser_zip_file_path)

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.perf_counter()
        return
    duration = time.perf_counter() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count*block_size*100/total_size),100)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

# downloads stanford parser
def download_parser_jar_file():
    stanford_parser_zip_file_path = os.environ.get('CLASSPATH') + ".jar"
    url = "https://nlp.stanford.edu/software/stanford-parser-full-2018-10-17.zip"
    urllib.request.urlretrieve(url, stanford_parser_zip_file_path, reporthook)

# extracts stanford parser
def extract_parser_jar_file():
    stanford_parser_zip_file_path = os.environ.get('CLASSPATH') + ".jar"
    try:
        with zipfile.ZipFile(stanford_parser_zip_file_path) as z:
            z.extractall(path=BASE_DIR)
    except Exception:
        os.remove(stanford_parser_zip_file_path)
        download_parser_jar_file()
        extract_parser_jar_file()

# extracts models of stanford parser
def extract_models_jar_file():
    stanford_models_zip_file_path = os.path.join(os.environ.get('CLASSPATH'), 'stanford-parser-4.2.0-models.jar')
    stanford_models_dir = os.environ.get('CLASSPATH')
    with zipfile.ZipFile(stanford_models_zip_file_path) as z:
        z.extractall(path=stanford_models_dir)


# checks jar file and downloads if not present 
def download_required_packages():
    if not os.path.exists(os.environ.get('CLASSPATH')):
        if is_parser_jar_file_present():
           pass
        else:
            download_parser_jar_file()
        extract_parser_jar_file()

    if not os.path.exists(os.environ.get('STANFORD_MODELS')):
        extract_models_jar_file()

