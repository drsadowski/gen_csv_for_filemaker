#! /usr/local/bin/python3
# generate a CSV file to be used to import PDF files into FileMaker
# this module assumes the PDF files exist and already follow our naming convention, 
# ie. ending in something like _1234.pdf
# after this is run, the files will be copied to the proper inventory folder
#   and then the csv file can be used with the proper filemaker table
import os
import csv
import argparse

def forfilemaker(thename, forpdf):
    dirpart = "Docs"
    if not forpdf:
        dirpart = "Pix"
    return 'image:Inventory {0}/{1}\nimagemac:/stem/Contents/General Information/Inventory/Inventory {0}/{1}'.format(dirpart, thename)

def find_extension(fname, extlist):
    for e in extlist:
        if fname.endswith(e):
            return e
    return None

# this is to generate the .csv used for import at a later date
def recompute_thepdfs(folder_with_files, is_pdf):
    extensions = [".pdf"]
    if not is_pdf:
        extensions = [".jpg", ".gif", ".jpeg", ".png"]
    thepdfs = []
    for root, dirs, files in os.walk(folder_with_files):
        for f in files:
            # we expect the names to end with a pattern like this "_1234.pdf"
            ext = find_extension(f, extensions)
            if ext == None:
                continue
            success = False
            fs = f[f.rfind('_') + 1: -len(ext)] # pull out the numeric suffix, which is the ID
            if not fs.isdigit(): # some files have a single letter suffix, eg. _1234a
                fs = fs[:-1] 
            if fs.isdigit():
                thepdfs.append({"k_ID_Inventory" : fs, 'Picture' : forfilemaker(f, is_pdf)})
                success = True
            if not success:
                print('file name problem:',f)
    return thepdfs

def save_pdf_names(thelist, new_csv_file):
    fout = open(new_csv_file, 'w', newline='', encoding='utf-8')
    fwriter = csv.DictWriter(fout, ['k_ID_Inventory','Picture'], dialect='unix')
    fwriter.writerow({'k_ID_Inventory':'k_ID_Inventory','Picture':'Picture'})
    for item in thelist:
        fwriter.writerow(item)
    fout.close()

def process_from_disk(thefiles, newcsv, is_pdf):
    thepdfs = recompute_thepdfs(thefiles, is_pdf)
    save_pdf_names(thepdfs, newcsv)

parser = argparse.ArgumentParser(description='Generate csv file for FileMaker import from PDFs or images')
parser.add_argument('sourcefolder', 
  help='folder with images, default="/Users/dan/Documents/images for inventory"; output will be foldername with .csv suffix', 
  default="/Users/dan/Documents/images for inventory", nargs='?')
parser.add_argument('-p', '--pix', help="look for Pix instead of PDFs", action="store_true")
args = parser.parse_args()

csvoutput = args.sourcefolder + '.csv'

process_from_disk(args.sourcefolder, csvoutput, not args.pix)
