from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import os
from pathlib import Path
from selenium.webdriver.chrome.options import Options

driver = webdriver.Chrome(executable_path= r"C:\Users\MARIA K\PycharmProjects\chromedriver.exe",chrome_options=options)


t = time.time()
driver.set_page_load_timeout(10)

try:
    driver.get('https://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones')
except TimeoutException:
    driver.execute_script("window.stop();")
print('Time consuming:', time.time() - t)


# Create emtpty list get the "specblue" elements, print them in a python list, and filter the empty strings and the strings with a blank space on them and rename them Keys
spec = driver.find_elements_by_class_name('specblue')
Keys = []
for i in spec:
    print (i.text)
    Keys.append(i.text)
filterKeys1 = [x for x in Keys if ( " " not in  x  ) ]
filtersKeys2 = [x for x in filterKeys1 if x != ""]
Keys= filtersKeys2


##---- until here !!!



keys = ['ECOPETROL', 'EXITO', 'CEMARGOS']

for key in keys:
    driver.find_element_by_id("nemo").send_keys(key)

    Buscar = driver.find_element_by_xpath("""//a[@href="javascript:document.busqueda.submit();"]""")
    Buscar.click()

    DateIn= driver.find_element_by_id("fechaIni")
    driver.execute_script("arguments[0].removeAttribute('readonly')", DateIn);
    DateIn.send_keys("10/10/2018")

    DateOut= driver.find_element_by_id("fechaFin")
    driver.execute_script("arguments[0].removeAttribute('readonly')", DateOut);
    DateOut.send_keys("03/15/2019")

    Descargar = driver.find_element_by_id("texto_3")
    Descargar.click()








