#!/usr/bin/python3


import cffi
from ctypes.util import find_library

PATH_TO_LIBTESS = '/usr/lib64/libtesseract.so'
TESS_DATA_DIR = '/usr/share/tesseract-ocr/4/tessdata/'

class tesseractApi:

    def __init__(self,lang='eng'):

        self.ffi = cffi.FFI()
        self.ffi.cdef("""
            
            typedef struct TessBaseAPI TessBaseAPI;
            typedef int BOOL;

            TessBaseAPI* TessBaseAPICreate();
            int TessBaseAPIInit3(TessBaseAPI* handle, const char* datapath, const char* language);

            typedef struct TessResultRenderer TessResultRenderer;
            TessResultRenderer* TessPDFRendererCreate(  const char* outputbase, const char* datadir, BOOL textonly );

            typedef struct TessPDFRenderer TessPDFRenderer;
            BOOL TessBaseAPIProcessPages(TessBaseAPI* handle,
                                        const char* filename,
                                        const char* retry_config,
                                        int timeout_millisec,
                                        TessResultRenderer* renderer);
           

        """)

        self.libtess = self.ffi.dlopen(PATH_TO_LIBTESS)
        self.api = self.libtess.TessBaseAPICreate()
        self.language = self.ffi.new("const char []",str.encode(lang))
        self.libtess.TessBaseAPIInit3(self.api, self.ffi.NULL, self.language)
        self.liblept = self.ffi.dlopen(find_library('lept'))
        

    def createPDFRenderer(self,outdata,txtonly=0):
        outputbase = self.ffi.new("const char []",str.encode(outdata))
        datadir = self.ffi.new("const char []",str.encode(TESS_DATA_DIR))
        renderer = self.libtess.TessPDFRendererCreate(outputbase,datadir,0)
        return renderer

    def processPDFPages(self,filename, outdata,txtonly=0,retry_config="",timeout_millisec=10000):
        renderer = self.createPDFRenderer(outdata,txtonly=0)
        self.libtess.TessBaseAPIProcessPages(self.api,str.encode(filename),str.encode(retry_config),timeout_millisec,renderer)