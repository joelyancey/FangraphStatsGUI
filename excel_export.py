from glob import glob
import logging
import traceback
import shutil
import sqlite3
from compile_db import *
cwd = os.getcwd()

'''
Changes:
- The original file removal loop was slow since it needs to scan the entire file index of the current 
directory 365 times, every time. The implementation below only scans the file index once, only 
requires any CPU time at all if files matching the glob pattern 'fangraph_*days.xlsx' exist.

'''

logger = logging.getLogger(__name__)

#delete all .xlsx files before compiling data

logger.info('Remove files')
for f in glob('fangraph_*days.xlsx'):
    shutil.rmtree(f)

for day in num_days:
    # insert the file path for the Excel wooksheet
    filePath = cwd + '/fangraph_{}days.xlsx'.format(day)

    # create SQLite connection with fangraph SQL database
    conn = sqlite3.connect(cwd + '/fangraph_{}days.db'.format(day))

    writer = pd.ExcelWriter(filePath, engine='xlsxwriter')

    df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
    print(df)

    for table_name in df['name']:
        sheet_name = table_name
        SQL = "SELECT * FROM " + sheet_name
        dft = pd.read_sql_query(SQL, conn)
        dft.to_excel(writer, sheet_name=sheet_name, index=False)

    writer.save()

