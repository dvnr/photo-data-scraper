"""
Install dependencies

!pip install selenium
!pip install webdriver_manager

!pip install selenium
!apt-get update # to update ubuntu to correctly run apt install
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
"""

import csv
import re
import requests
import sys
import time
from urllib.request import Request, urlopen

sys.path.insert(0, "/usr/lib/chromium-browser/chromedriver")
from selenium import webdriver
from bs4 import BeautifulSoup

###
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

from photo_data.local import foto_url_pattern, foto_type

###
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-dev-shm-usage")

###
new_row = []
now = time.strftime('%Y-%m-%d %H:%M:%S')

def main():
    with open('photo_data/photographers-ids-test.csv', 'r') as in_file, open('output.csv', 'w') as out_file:
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)

        writer.writerow(
            [
                "id",
                "type",
                "name",
                "bio",
                "gnd",
                "photo_fonds",
                "photo_exh_solo",
                "photo_exh_group",
                "photo_context",
            ]
        )

        #for foto_id in range(
        #    20473, 20474
        #):  # IDs range – use "20473-20474" for testing purposes
        for row in reader:
            foto_id = row[0]

            print(foto_id, end=" ")

            foto_url = foto_url_pattern.replace("[foto_id]", str(foto_id))

            photo_name = ""
            photo_bio = ""
            photo_gnd = ""
            photo_context = ""

            photo_fonds_list = []
            photo_exh_solo_list = []
            photo_exh_group_list = []

            # Create a new Firefox browser object
            browser = webdriver.Chrome("chromedriver", options=chrome_options)

            try:
                browser.get(foto_url)
                time.sleep(2)

                # Create BeautifulSoup object from page source.
                page = BeautifulSoup(browser.page_source, "html.parser")

                # Modal windows
                modals = page.select("div.modal-content")

                for modal in modals:
                    photo_name = modal.select("h1.ng-binding")[0].text.strip()
                    photo_bio = modal.select("h4.ng-binding")[0].text.strip()

                    
                    print(photo_name)
                    
                    ###########
                    # Context #
                    ###########
                    try:
                        photo_context = modal.select("content-raw[ng-if*='detail.umfeld']")
                        photo_context = str(photo_context).replace("\n", " ")
                    except:
                        pass

                    #######
                    # GND #
                    #######
                    print("GND...", end=" ")
                    if len(modal.select("a[href*=gnd]")) > 0:
                        photo_gnd = modal.select("a[href*=gnd]")[0].text.strip()
                        print("Ok")

                    #########
                    # Fonds #
                    #########
                    print("Fonds...", end=" ")
                    try:
                        button_toggle_panel = browser.find_element_by_link_text("Fonds")
                    except:
                        pass
                    try:
                        button_toggle_panel.click()
                        time.sleep(1)

                        div_links = modal.select("inventory-reference")
                        div_link = div_links[0]
                        # link_list = div_link.findAll("div[class='list__item__title']")
                        link_list = div_link.find_all("div", class_="list__item__title")

                        if len(link_list) > 0:
                            for link in link_list:

                                # Clicca link
                                browser.find_element_by_partial_link_text(
                                    link.text.strip()
                                ).click()
                                time.sleep(0.800)

                                # Ottieni URL
                                browser.switch_to.window(browser.window_handles[0])
                                urltemp = browser.current_url
                                urltodownload = requests.get(urltemp)
                                urltodownload = urltodownload.url
                                photo_fonds_list.append(urltodownload)

                                # Ottieni info
                                sub_page = BeautifulSoup(browser.page_source, "html.parser")
                                rows = sub_page.select("div.modal-content")
                                for row in rows:
                                    item_name = row.select("h1.ng-binding")[0].text.strip()
                                    # print(item_name)

                                # Clicca "Back"
                                browser.find_element_by_xpath(
                                    "//a[@class='go-back ng-binding']"
                                ).click()
                                time.sleep(0.800)
                        print("Ok")
                    except:
                        pass

                    ####################
                    # Solo exhibitions #
                    ####################
                    print("Solo...", end=" ")
                    try:
                        button_toggle_panel = browser.find_element_by_link_text(
                            "Single exhibition"
                        )
                    except:
                        pass
                    try:
                        button_toggle_panel.click()
                        time.sleep(1)

                        div_links = modal.select(
                            "default-list[values='detail.einzelausstellungen']"
                        )
                        div_link = div_links[0]
                        link_list = div_link.findAll("a")

                        if len(link_list) > 0:
                            for link in link_list:

                                # Clicca link
                                browser.find_element_by_link_text(link.text).click()
                                time.sleep(0.800)

                                # Ottieni exh URL
                                browser.switch_to.window(browser.window_handles[0])
                                urltemp = browser.current_url
                                urltodownload = requests.get(urltemp)
                                urltodownload = urltodownload.url
                                photo_exh_solo_list.append(urltodownload)

                                # Ottieni exh info
                                exh_page = BeautifulSoup(browser.page_source, "html.parser")
                                rows = exh_page.select("div.modal-content")
                                for row in rows:
                                    exh_name = row.select("h1.ng-binding")[0].text.strip()
                                    # print(exh_name)

                                # Clicca "Back"
                                browser.find_element_by_xpath(
                                    "//a[@class='go-back ng-binding']"
                                ).click()
                                time.sleep(0.800)
                        print("Ok")
                    except:
                        print("—")
                        pass

                    #####################
                    # Group exhibitions #
                    #####################
                    print("Group...", end=" ")
                    try:
                        button_toggle_panel = browser.find_element_by_link_text(
                            "Group exhibition"
                        )
                    except:
                        pass
                    try:
                        button_toggle_panel.click()
                        time.sleep(1)

                        div_links = modal.select(
                            "default-list[values='detail.gruppenausstellungen']"
                        )
                        div_link = div_links[0]
                        link_list = div_link.findAll("a")

                        if len(link_list) > 0:
                            for link in link_list:

                                # Clicca link
                                browser.find_element_by_link_text(link.text).click()
                                time.sleep(0.800)

                                # Ottieni URL
                                browser.switch_to.window(browser.window_handles[0])
                                urltemp = browser.current_url
                                urltodownload = requests.get(urltemp)
                                urltodownload = urltodownload.url
                                photo_exh_group_list.append(urltodownload)

                                # Ottieni info
                                exh_page = BeautifulSoup(browser.page_source, "html.parser")
                                rows = exh_page.select("div.modal-content")
                                for row in rows:
                                    exh_name = row.select("h1.ng-binding")[0].text.strip()


                                # Clicca "Back"
                                browser.find_element_by_xpath(
                                    "//a[@class='go-back ng-binding']"
                                ).click()
                                time.sleep(0.800)
                        print("Ok")
                    except:
                        print("—")
                        pass

                    new_row = [
                        foto_id,
                        foto_type,
                        photo_name,
                        photo_bio,
                        photo_gnd,
                        photo_fonds_list,
                        photo_exh_solo_list,
                        photo_exh_group_list,
                        photo_context,
                    ]

                    writer.writerow(new_row)

            finally:
                browser.quit()

if __name__ == '__main__':
    main()