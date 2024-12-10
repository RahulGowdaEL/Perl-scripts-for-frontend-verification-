import os
import sys
import pandas as pd
import argparse
import xlrd
import logging
import numpy as np
logging.basicConfig(format='%(asctime)s : %(levelname)s : [%(filename)s:%(lineno)d]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
NaN = np.nan
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description = "Sanity check liblist for inaccurate demet paths for PA simulation")
    parser.add_argument('-liblist','--liblist', required = True, type = str, help = "Provide full path for the Liblist file")
    parser.add_argument('-out_dir','--output_dir',default = os.getcwd(), required = True, type = str, help = "Path where report is dumped")
    parser.add_argument('-demet_list','--demet_list',type=str, help = 'Provide demet std cell signature',required = True)
    args = parser.parse_args()
    return args

def sanity_check (liblist,outDir,std_cells):
    with open(liblist,'r') as fp:
        libs = fp.read().splitlines();
    
    demet_libs = []
    for lib in libs:
        if (any(demet in lib for demet in std_cells)):
            demet_libs.append(lib)

    report_list = []
    for demet_lib in demet_libs:
        if("partl_ret_demet" not in str(demet_lib)):
            report_list.append(demet_lib)
    report_list = set(report_list)
    logger.debug(libs)
    logger.debug(demet_libs)
    
    if not report_list:
        print('\n')
        logger.info("Liblist appears to be correct for the given std cells")
    else:
        print('\n')
        logger.error("Below Lib files can be coming from incorrect path. Please review\n")
        print(*report_list,sep = "\n")
        #report_list.insert(0,"ERROR: Below Lib files can be coming from incorrect path. Please review\n")
        with open(os.path.join(outDir,'error.log'),'w+') as fp:
            fp.write('\n'.join(report_list))
        	    

if __name__ == '__main__':
    args = parse_arguments()
    liblist = args.liblist
    outDir = args.output_dir
    demet_list = args.demet_list
    #print(demet_list) 
    if (os.path.isfile(demet_list)):
        with open(demet_list,'r') as fp:
            std_cells = fp.read().splitlines()
            std_cells = [cell.replace(' ','') for cell in std_cells if cell !='']
            std_cells = ['_'+cell.split('_')[0] for cell in std_cells]
            std_cells = list(set(std_cells))
            #print(std_cells)
    else:
        print("Error: Demet list doesn't exist")
  
    sanity_check(liblist,outDir,std_cells)
