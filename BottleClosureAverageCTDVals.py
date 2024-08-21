
##################################################################################################
# python program = BottleClosureAverageCTDVals.py
#################################################
# The program will average CTD data from bottle closures to 4 seconds (user editable) before each bottle closure.
# This program will take derived CTD data that has been processed using SBE software per CalCOFI's guidelines. 
# The derived data will already need to be in an .asc file (again per the CalCOFI instructions). 
# You will also need to have the .bl file for the cast. 
# It uses the .bl file to get the bottle closure scan number and is currently coded to use the beginning scan. 
# It will produce a new .csv file with "_btlAvgd.csv" appended to the end - copying the formatting of the .asc filenaming structure. 
# The new averaged CTD values can be used to compare with the chemically analyzed bottle values.    
# The program is designed to place the generated "..._btlAvgd.csv" file in the same directory as the selected .asc file. 
# I've programmed this on a Windows 10 machine, and and have not yet tested it on macOS or Linux.
# --> Until further notice, modifications may be needed to run on macOS or Linux. 
# The program currently only processes one .asc and .bl file at a time, 
# though I plan to modify the program to process multiple derived cast files at once. 
##################################################################################################

from decimal import Decimal
from multiprocessing import parent_process
from pathlib import Path
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import numpy as np
import os

##################################################################################################

defaultPath = "/"
ascPath = None
ascParent = None    # To check if the asc and bl are from the same parent directory before processing. 
blPath = None
blParent = None    # To check if the asc and bl are from the same parent directory before processing. 
blCsvTempPath = ""
resultPath = None
ascFilename = ""
resultFilename = ""
result = pd.DataFrame()

##################################################################################################
def browseFilesAsc():
    global defaultPath
    global ascPath
    global ascParent
    global ascFilename

    ascPath = filedialog.askopenfilename(initialdir = defaultPath,
                                          title = "Select a File",
                                          filetypes = (("ASC files",
                                                        "*.asc*"),
                                                       ("all files",
                                                        "*.*")))
    ascFilename = Path(ascPath).name
    display_selected_ascFile.configure(text="" +ascFilename, anchor="w")    
    ascParent = Path(ascPath).parent
    defaultPath = ascParent.absolute().as_posix()
    display_asc_fullpath.configure(text="" +ascPath, anchor="w")
    
############################################
def browseFilesBl():
    global defaultPath      # This is required to update a global in python. 
    global blPath
    global blParent
    blPath = filedialog.askopenfilename(initialdir = defaultPath,
                                          title = "Select a File",
                                          filetypes = (("BL files",
                                                        "*.bl*"),
                                                       ("all files",
                                                        "*.*")))
    filename = Path(blPath).name
    display_selected_blFile.configure(text="" +filename, anchor="w")
    blParent = Path(blPath).parent
    defaultPath = blParent.absolute().as_posix()
    display_bl_fullpath.configure(text="" +blPath)


############################################
# Convert bl to CSV - The pandas library needs a .csv file, and the .bl has invalid data non-csv data in the first 2 rows. 
def blToCSV():
    global blCsvTempPath 

    blCsvTempPath = os.path.join(blParent,"blTemp.csv")
    fout = open(blCsvTempPath, "w+")   # This temp file is deleted upon program closure. 
    with open(blPath, 'r') as fp:
        # Excludes the first 2 rows of the file which are NOT csv. 
        text = fp.read().splitlines(True)[2:]
        fout.writelines(text)
    fp.close()

############################################

def createAverages():
    global ascFilename
    global ascPath
    global blCsvTempPath
    global result
    global resultPath
    global resultFilename
    
    blToCSV()

    blData = pd.read_csv(blCsvTempPath, header=None,)
    
    #Delete the temp CSV file. 
    if os.path.exists(blCsvTempPath):
        os.remove(blCsvTempPath)
        print(f"Temp file {blCsvTempPath} has been deleted.")
    
    BTL_FIRE_SEQ_COL = 0
    BTL_NUM_COL = 1
    START_SCAN_COL = 3

    secToAvg = int(spin_Number.get())
    scansToAverage = secToAvg * 24 
    bottlesRange = blData.shape[0]

    ascData = pd.read_csv(ascPath, encoding='latin-1')

    #Drop DATETIME field from averaging. 
    ascData = ascData.drop(ascData.columns[1], axis=1)
 
    for btl in range(bottlesRange):
        scanCollection = []
        startScan = blData.loc[btl, START_SCAN_COL]
        backScan = int(startScan - scansToAverage + 1)
        backScanOriginal = backScan

        while(backScan <=startScan):            
            scanCollection.append(backScan)
            backScan +=1

        allScansData = ascData.loc[ascData['Scan'].isin(scanCollection)]
        
        #Below excludes the columns for scan number and date from the mean calclations. 
        #mean = allScansData.iloc[:, 1:].mean(axis=0)
        mean = allScansData.mean(axis=0)
        mean = mean.to_frame().T
       
        # drop the scans column
        mean = mean.drop(mean.columns[0], axis=1) 

        mean.insert(0, 'Btl', " ")
        mean.insert(1, 'SecAvgd', " ")
        mean.insert(2, 'StartScan', " ")
        mean.insert(3, 'BackScan', " ")

        #Adds bottle, seconds, and scan info as a recerence.
        # Note: since the mean datafram only ever has 1 row, row is ALWAYS set to zero. 
        mean.loc[0, 'Btl'] = blData.loc[btl, BTL_NUM_COL]
        mean.loc[0, 'SecAvgd'] = secToAvg
        mean.loc[0, 'StartScan'] = startScan
        mean.loc[0, 'BackScan'] = backScanOriginal

       # If result is empty, have it's structure set to mean
        if result.empty:
            result.reindex_like(mean)

        result = pd.concat([result, mean], sort=False)
    
    # Once out of the loop:
    # Write result to file.
    

   

    resultFilename = ascFilename[:-4] + "_btlAvgd.csv"
    resultPath = os.path.join(ascParent, resultFilename)
    result.to_csv(resultPath, index=False, sep=',')
    display_created_file.configure(text="" +resultFilename)
    display_created_fullpath.configure(text="" +resultPath)

##################################################################################################   

def goToFile():
    myPath = Path(resultPath).parent
    
    try:
        # Windows
        if os.name == 'nt':
            os.startfile(myPath)
        # macOS
        elif os.uname().sysname == 'Darwin':
            subprocess.run(['open', myPath])
        # Linux
        else:
            subprocess.run(['xdg-open', myPath])
    except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")
######################################################

def clearAll(): 
    global ascPath
    global blPath 
    global resultPath
    
    display_asc_fullpath.configure(text="" )
    display_selected_ascFile.configure(text="")
    display_selected_blFile.configure(text="")
    display_bl_fullpath.configure(text="")
    display_created_file.configure(text="")
    display_created_fullpath.configure(text="")
    ascPath = None
    blPath = None
    resultPath = None
######################################################

def on_closing():
    global blCsvTempPath

    # Perform any cleanup here
    print("Window is closing. Performing cleanup...")
    # if os.path.exists(blCsvTempPath):
    #     os.remove(blCsvTempPath)
    #     print(f"Temp file {blCsvTempPath} has been deleted.")
    # else:
    #     print("Found no temporary file to Delete.")

    window.destroy() 

##################################################################################################
window = Tk()
window.title("Get Bottle Closure Average CTD Vals")
window.geometry('900x325')
window.protocol("WM_DELETE_WINDOW", on_closing)

##################################################################################################
# Clear All Fields Button
button_clearAll = Button(window, text = "Clear All", command = clearAll) 
button_clearAll.grid(column=0, row=0, sticky="w")

############################################
# Select Derived ASCII asc File for CTD data
label_file_explorer = Label(window, text="Select Derived ASCII .asc File: ")                      
label_file_explorer.grid(column=0,row=1, sticky="e")

button_asc_explore = Button(window, text = "Browse Files", command = browseFilesAsc) 
button_asc_explore.grid(column = 1, row = 1)

display_selected_ascFile = Label(window, text="", anchor="w", fg = "blue")                            
display_selected_ascFile.grid(column=2,row=1, sticky="w")

label_asc_fullpath = Label(window, text = "Full Path: ")
label_asc_fullpath.grid(column = 1, row = 2, sticky="e")

display_asc_fullpath = Label(window, text="", anchor="w", fg = "blue") 
display_asc_fullpath.grid(column=2, row=2, sticky="w")

############################################
# Select bl file for bottle closure scan number and time information. 
lbl = Label(window, text="Select .bl file: ")
lbl.grid(column=0, row=3, sticky="e")

button_bl_explore = Button(window, text = "Browse Files", command = browseFilesBl) 
button_bl_explore.grid(column = 1, row = 3)

display_selected_blFile = Label(window, text="", anchor="w", fg = "Green")                            
display_selected_blFile.grid(column=2,row=3, sticky="w")

label_bl_fullpath = Label(window, text = "Full Path: ")
label_bl_fullpath.grid(column = 1, row = 4, sticky="e")

display_bl_fullpath = Label(window, text="", anchor="w", fg = "Green") 
display_bl_fullpath.grid(column=2, row=4, sticky="w")

############################################
# Select seconds before bottle closure

label_seconds_before = Label(window, text="Seconds before bottle trip: ") 
label_seconds_before.grid(column=0, row=5, sticky="e")

seconds = IntVar(value=4)
spin_Number = Spinbox(window, from_ = 0, to =500, textvariable=seconds, width=10)
spin_Number.grid(column=1, row=5)

############################################
# Empty row for spacing 
label_empty = Label(window, text="")
label_empty.grid(column=0, row=6, sticky="")

############################################
# Create 4 second averages
button_create_averages = Button(window, text = "Create Bottle Closure CTD Averages", command=createAverages)
button_create_averages.grid(column=2, row=7, sticky="w")

############################################
# Results  
label_empty = Label(window, text="File Created: ") 
label_empty.grid(column=1, row=8, sticky="e")

display_created_file = Label(window, text="", anchor="w", fg = "Brown")                            
display_created_file.grid(column=2,row=8, sticky="w")

label_created_fullpath = Label(window, text = "Full Path: ")
label_created_fullpath.grid(column = 1, row = 9, sticky="e")

display_created_fullpath = Label(window, text="", anchor="w", fg = "Brown")                            
display_created_fullpath.grid(column=2,row=9, sticky="w")                            

############################################
# Go to file
button_goToFile = Button(window, text = "Go to created file", command=goToFile)
button_goToFile.grid(column=2, row=10, sticky="w")

############################################
# Empty row for spacing 
label_empty = Label(window, text="")
label_empty.grid(column=0, row=11, sticky="")

############################################
# Empty row for spacing 
label_empty = Label(window, text="")
label_empty.grid(column=0, row=12, sticky="")

############################################
# Exit Program Button
button_Exit = Button(window, text = "Exit Program", command = on_closing) 
button_Exit.grid(column=0, row=13, sticky="w")

window.mainloop()