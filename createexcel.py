import pandas as pd
import numpy as np
from openpyxl import load_workbook
import os

book = load_workbook("data.xlsx")
excelWriter = pd.ExcelWriter("data.xlsx")
excelWriter.book = book

for file in os.listdir("out/"):
    data = pd.read_csv("out/"+file)
    data.to_excel(excelWriter, sheet_name = file)

excelWriter.save()
excelWriter.close()