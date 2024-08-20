
#Python program = BottleClosureAverageCTDVals.py

This program will take derived CTD data that has been processed using SBE software per CalCOFI's guidelines. 

The derived data will already need to be in an .asc file (again per the CalCOFI instructions). 

You will also need to have the .bl file for the cast. 

The program will average data from bottle closure to 4 seconds (user editable) before the bottle closure.

It uses the .bl file to get the bottle closure scan number and is currently coded to use the beginning scan. 

It will produce a new .csv file with "_btlAvgd.csv" appended to the end - copying the formatting of the .asc filenaming structure. 

The new averaged CTD values can be used to compare with the chemically analyzed bottle values.    

The program is designed to place the generated "..._btlAvgd.csv" file in the same directory as the selected .asc file. 

I've programmed this on a Windows 10 machine, and and have not yet tested it on macOS or Linux.

The program currently only processes one .asc and .bl file at a time, 

Though I plan to modify the program to process multiple derived cast files at once. 

