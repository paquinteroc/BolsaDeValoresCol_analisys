# 1/28/2020
# Download all historical stocks data from the website page and concatenate the excel files in 'All_Stocks_historical.csv'

from selenium import webdriver
from bs4 import BeautifulSoup
import request
import datetime
import time
import pandas as pd
import os, glob
import xlrd
import openpyxl
from pathlib import Path
from selenium.webdriver.chrome.options import Options


## Set the folder where to download ##
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": r"C:\Users\MARIA K\Documents\bvc_doownload",
  "download.prompt_for_download": False,
})

driver = webdriver.Chrome(executable_path= r"C:\Users\MARIA K\PycharmProjects\chromedriver.exe",
                          chrome_options=chrome_options) # Set the driver
t = time.time()
driver.set_page_load_timeout(10) # max time to load website

try:
    driver.get('https://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones')
except TimeoutException:
    driver.execute_script("window.stop();")
print('Time consuming:', time.time() - t)

#dates!

format = '%Y-%m-%d' #format used on the website
today = datetime.date.today()   # today
s = today.strftime(format)
delta_five_months = datetime.timedelta(5*365/12) #delta of 4 months
previous_date = today - delta_five_months
print(today.strftime(format))
print(previous_date.strftime(format))

#Insert complete path to the excel file and index of the worksheet
df1 = pd.read_csv(r'C:\Users\MARIA K\PycharmProjects\BolsaDeValoresCol_analisys\ListofStocks.csv')
# insert the name of the column as a string in brackets sheet_name=0
keys = df1[df1.columns[0]].to_list()
print(keys)

for key in keys:
    print(key)
    driver.find_element_by_id("nemo").clear()
    driver.find_element_by_id("nemo").send_keys(key)

    Buscar = driver.find_element_by_xpath("""//a[@href="javascript:document.busqueda.submit();"]""")
    Buscar.click()

    date_hasta = today
    date_desde = today - delta_five_months


    for i in range(10):

        DateIn= driver.find_element_by_id("fechaIni")
        driver.execute_script("arguments[0].removeAttribute('readonly')", DateIn);
        DateIn.send_keys(date_desde.strftime(format))

        DateOut= driver.find_element_by_id("fechaFin")
        driver.execute_script("arguments[0].removeAttribute('readonly')", DateOut);
        DateOut.send_keys(date_hasta.strftime(format))

        Descargar = driver.find_element_by_id("texto_3")
        Descargar.click()
        driver.refresh()

        date_hasta = date_desde
        date_desde = date_hasta - delta_five_months
        print(i)



### Work with excel files

path = r"C:\Users\MARIA K\Documents\bvc_doownload"
excel_names = os.listdir(path)
print(excel_names)

#ho # current folder
os.chdir(path) # change folder or change path
# read them in
excels = [pd.ExcelFile(names) for names in excel_names]
frames = [x.parse(x.sheet_names[0], header=None, index_col=None) for x in excels]

# delete the first row for all frames except the first
# i.e. remove the header row -- assumes it's the first
frames[1:] = [df[2:] for df in frames[1:]]

# concatenate them..
combined = pd.concat(frames)
combined.drop(combined.columns[0], axis=1, inplace=True)
combined.to_csv("All_Stocks_historical.csv", header=False, index=False)

