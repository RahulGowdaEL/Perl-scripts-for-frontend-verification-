import os
import argparse
import logging
import numpy as np

# Setup logging configuration
logging.basicConfig(format='%(asctime)s : %(levelname)s : [%(filename)s:%(lineno)d]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
NaN = np.nan

def parse_arguments():
    parser = argparse.ArgumentParser(description="Sanity check liblist for inaccurate demet paths for PA simulation")
    parser.add_argument('-liblist', '--liblist', required=True, type=str, help="Provide full path for the Liblist file")
    parser.add_argument('-out_dir', '--output_dir', default=os.getcwd(), type=str, help="Path where report is dumped")
    parser.add_argument('-demet_list', '--demet_list', type=str, help='Provide demet std cell signature', required=True)
    return parser.parse_args()

def sanity_check(liblist, out_dir, std_cells):
    # Read library list file
    try:
        with open(liblist, 'r') as fp:
            libs = fp.read().splitlines()
    except Exception as e:
        logger.error(f"Failed to read liblist file: {e}")
        return

    # Find libraries containing demet cells
    demet_libs = [lib for lib in libs if any(demet in lib for demet in std_cells)]

    # Identify problematic libraries
    report_list = [lib for lib in demet_libs if "partl_ret_demet" not in lib]
    report_list = list(set(report_list))  # Remove duplicates

    # Logging and reporting
    if not report_list:
        logger.info("Liblist appears to be correct for the given std cells")
    else:
        logger.error("Below Lib files may have incorrect paths. Please review:")
        for lib in report_list:
            print(lib)
        # Write the report to an error log
        try:
            error_log_path = os.path.join(out_dir, 'error.log')
            with open(error_log_path, 'w') as fp:
                fp.write('\n'.join(report_list))
            logger.info(f"Error log written to {error_log_path}")
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")

if __name__ == '__main__':
    # Parse arguments
    args = parse_arguments()
    liblist = args.liblist
    out_dir = args.output_dir
    demet_list = args.demet_list

    # Validate demet list file
    if os.path.isfile(demet_list):
        try:
            with open(demet_list, 'r') as fp:
                std_cells = fp.read().splitlines()
                std_cells = [cell.strip() for cell in std_cells if cell.strip()]  # Remove spaces and empty lines
                std_cells = ['_' + cell.split('_')[0] for cell in std_cells]  # Add underscore and take prefix
                std_cells = list(set(std_cells))  # Remove duplicates
        except Exception as e:
            logger.error(f"Failed to process demet list: {e}")
            sys.exit(1)
    else:
        logger.error("Error: Demet list file doesn't exist")
        sys.exit(1)

    # Perform sanity check
    sanity_check(liblist, out_dir, std_cells)
