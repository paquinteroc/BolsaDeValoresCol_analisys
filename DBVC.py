from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import datetime
import time
import pandas as pd
import os,glob
from pathlib import Path
from selenium.webdriver.chrome.options import Options

## Set the folder where to download ##
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": r"C:\Users\paquinte\PycharmProjects\BolsaDeValoresCol_analisys",
  "download.prompt_for_download": False,
})

driver = webdriver.Chrome(executable_path= r"C:\Users\paquinte\Documents\chromedriver.exe",
                          chrome_options=chrome_options) # Set the driver
t = time.time()
driver.set_page_load_timeout(10) # max time to load website

try:
    driver.get('https://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones')
except TimeoutException:
    driver.execute_script("window.stop();")
print('Time consuming:', time.time() - t)


# Create emtpty list get the "specblue" elements, print them in a python list, and filter the empty strings and the strings with a blank space on them and rename them Keys
# spec = driver.find_elements_by_class_name('specblue')
# Keys = []
# for i in spec:
#     print (i.text)
#     Keys.append(i.text)
# filterKeys1 = [x for x in Keys if ( " " not in  x  ) ]
# filtersKeys2 = [x for x in filterKeys1 if x != ""]
# Keys= filtersKeys2


##---- until here !!!

format = '%Y-%m-%d' #format used on the website
today = datetime.date.today()   # today
s = today.strftime(format)
delta_five_months = datetime.timedelta(5*365/12) #delta of 4 months
previous_date = today - delta_five_months
print(today.strftime(format))
print(previous_date.strftime(format))



keys = ['ECOPETROL', 'EXITO', 'CEMARGOS']

key= 'ECOPETROL'
for key in keys:
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


for file in glob.glob("*.xls"):
    print(file)


excel_names = ["xlsx1.xlsx", "xlsx2.xlsx", "xlsx3.xlsx"]

# read them in
excels = [pd.ExcelFile(name) for name in glob.glob("*.xls")]

# turn them into dataframes
# frames = [x.parse(x.sheet_names[0], header=None,index_col=None) for x in excels]
 frames = [x.parse(x.sheet_names[0],header=, index_col=None) for x in excels]
frames = [ pd.read_excel(x,header=1) for x in excels]

type(frames[1])
frames[1].columns
frames.size
# delete the first row for all frames except the first
# i.e. remove the header row -- assumes it's the first
frames[1:] = [df[1:] for df in frames[1:]]

# concatenate them..
combined = pd.concat(frames)
combined.fecha.max()
combined.fecha.min()
combined.shape

combined.drop(combined.columns[0],axis=1, inplace=True)

combined.head()

combined.to_csv("All_Stocks_historical.csv")
