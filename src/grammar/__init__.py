import os
from textx import language, metamodel_from_file

def get_metamodel():
    curr_dir = os.path.dirname(__file__)
    grammer_path = os.path.join(curr_dir, 'slika.tx')
    return metamodel_from_file(grammer_path)

@language('slika',"*.sl")
def slika_language():
    return get_metamodel()