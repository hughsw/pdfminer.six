#!/usr/bin/env python3

# Exercise pdfminer, looking deeply into a PDF document, print some stats to stdout
# Usage: parsepdf0.py <PDF filename>

import sys, os
import collections

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTContainer


_, SCRIPT = os.path.split(__file__)

def msg(*args, **kwargs):
    print(' '.join(map(str, args)), file=sys.stdout, **kwargs)

def flat_iter(obj):
    yield obj
    if isinstance(obj, LTContainer):
        for ob in obj:
            yield from flat_iter(ob)

def main(args):
    msg(SCRIPT, args)

    if len(args) != 1:
        msg('Parse a PDF file and print some pdfminer-specific stats')
        msg('Usage:', SCRIPT, '<PDF filename>')
        return 1

    infilename, = args

    lt_types = collections.Counter()

    with open(infilename, 'rb') as pdf_file:

        # Create a PDF parser object associated with the file object.
        parser = PDFParser(pdf_file)

        # Create a PDF document object that stores the document structure.
        # Supply the password for initialization.
        password = ''
        document = PDFDocument(parser, password)
        # Check if the document allows text extraction.
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed(filename)

        # Make a page iterator
        pages = PDFPage.create_pages(document)


        # Set up for some analysis
        rsrcmgr = PDFResourceManager()
        laparams = LAParams(
            detect_vertical=True,
            all_texts=True,
            )
        #device = PDFDevice(rsrcmgr)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Look at all (nested) objects on each page
        for page_count, page in enumerate(pages, 1):
            # oh so stateful
            interpreter.process_page(page)
            layout = device.get_result()

            for item in flat_iter(layout):
                lt_types[type(item).__name__] += 1

    msg('page_count', page_count)
    msg('lt_types:', ' '.join('{}:{}'.format(*tc) for tc in lt_types.items()))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
