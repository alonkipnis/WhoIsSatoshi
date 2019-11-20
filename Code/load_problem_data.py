import os
import re
import glob
import codecs
import pandas as pd
from tqdm import tqdm
from text_processing import *

#PDF miner
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io

def convert_pdf_to_txt(path_to_file):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path_to_file, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                  password=password, caching=caching,
                                  check_extractable = True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

def load_dir(path) :
    lo_texts = pd.DataFrame()
    pdf_files = glob.glob(path + "*.pdf")
    txt_files = glob.glob(path + "*.txt")
    html_files = glob.glob(path + "*.html") + glob.glob(path + "*.htm")

    for fn in pdf_files : 
        try :
            txt = convert_pdf_to_txt(fn)
            lo_texts = lo_texts.append({'doc_id' : fn.split('/')[-1], 'text' : txt}, ignore_index = True )
        except :
            print("could not load {} or convert it to a text file".format(fn))

    for fn in txt_files : 
        try :
            f = codecs.open(fn,'r',encoding='utf-8', errors='ignore')
            txt = f.read()    
            f.close()
            lo_texts = lo_texts.append({'doc_id' : fn.split('/')[-1], 'text' : txt}, ignore_index = True)
        except : 
            print("could not load {}".format(fn))

    for fn in html_files : 
        try : 
            f = codecs.open(fn,'r',encoding='utf-8', errors='ignore')
            txt = f.read()    
            f.close()  
            lo_texts = lo_texts.append({'doc_id' : fn.split('/')[-1], 'text' : txt}, ignore_index = True )
        except :
            print("could not load {}".format(fn))
    
    return lo_texts


def load_problem_data(path, include_subdir = True) :
    df = pd.DataFrame()
    lo_dirs = glob.glob(path + "*/")
    
    for dirc in tqdm(lo_dirs) :
        author_name = dirc.split('/')[-2]
        lo_sub_dir = glob.glob(dirc + "*/")
        for sub_dir in lo_sub_dir :
            label = sub_dir.split('/')[-2]
            try :
                df1 = load_dir(sub_dir)
                df1.loc[:,'author'] = author_name
                df1.loc[:,'type'] = label
                df = df.append(df1, ignore_index=True)
            except :
                print("Error loading {}".format(dirc))
    
    return df

if __name__ == "__main__":
    # execute only if run as a script
	data = load_problem_data("/Users/kipnisal/Dropbox/WhoIsSatoshi/")
	data_proc = data.copy()
	data_proc.text = data.text.astype(str).\
				apply(lambda x : preprocess_text(x, stem = True,
                                     remove_proper_names = True,
                                        remove_html_tags = True,
                                           remove_digits = True ))
	data_proc.to_csv('data.csv')

