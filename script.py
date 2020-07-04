import os
import sys
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup():
    person = sys.argv[1]
    print(f"person: {person}")
    load_dotenv(f"./.envs/.{person}")
    print(f"email: {os.getenv('EMAIL')}")

class FitDriver:
    def __init__(self):
        if sys.platform == "win32":
            chromedriver_path = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        else:
            chromedriver_path = "chromedriver"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)
        self.driver.implicitly_wait(10)

    def click_button(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def login(self):
        try:
            self.driver.get('https://myfit4less.gymmanager.com/portal/booking/index.asp?id=welcome')
            login_title_elem = self.driver.find_element_by_xpath('//*[@id="API"]/h1')
            email_elem = self.driver.find_element_by_xpath('//*[@id="emailaddress"]')
            email_elem.clear()
            email_elem.send_keys(os.getenv("EMAIL"))
            pw_elem = self.driver.find_element_by_xpath('//*[@id="password"]')
            pw_elem.clear()
            pw_elem.send_keys(os.getenv("PASSWORD"))
            login_button = self.driver.find_element_by_id("loginButton")
            self.click_button(login_button)
            print("Logged in successfully")
        except NoSuchElementException as ex:
            print(ex)
            print("Already logged in")
        except Exception as ex:
            print(ex)
            print("Login failed")

    def check_for_date_select(self):
        uh_oh = False
        try:
            select_day_button = self.driver.find_element_by_id('btn_date_select')
            reserved_slots = self.driver.find_element_by_class_name('reserved-slots')
            slots_list = reserved_slots.find_elements_by_class_name('time-slot')
            already_booked = []
            for elem in slots_list:
                booking_info = elem.get_property("dataset")
                # Format: 'Friday, 26 June 2020'
                already_booked.append(booking_info['slotdate'].upper())
            self.click_button(select_day_button)
            modal_dates = self.driver.find_element_by_id('modal_dates')
            modal_dialog = modal_dates.find_element_by_class_name('modal-dialog')
            modal_content = modal_dialog.find_element_by_class_name('modal-content')
            modal_body = modal_dialog.find_element_by_class_name('modal-body')
            dates_to_choose = modal_body.find_element_by_class_name('dialog-content')
            dates_list = dates_to_choose.find_elements_by_class_name('button')

            # THIS PART IS bad RN AND try_to_book()
            for elem in reversed(dates_list):
                date = elem.get_property("innerText")
                if date not in already_booked:
                    try:
                        close_button = self.driver.find_element_by_id('dialog_date_close')
                        self.click_button(close_button)
                    except:
                        pass
                    self.try_to_book(date)

        except NoSuchElementException as ex:
            print("Can't select date. Either uh oh or max resos")
            uh_oh = True
        return uh_oh

    def try_to_book(self, date):
        def sort_key(e):
            return e.get_property("dataset")["slottime"]
        select_day_button = self.driver.find_element_by_id('btn_date_select')
        self.click_button(select_day_button)
        modal_dates = self.driver.find_element_by_id('modal_dates')
        modal_dialog = modal_dates.find_element_by_class_name('modal-dialog')
        modal_content = modal_dialog.find_element_by_class_name('modal-content')
        modal_body = modal_dialog.find_element_by_class_name('modal-body')
        dates_to_choose = modal_body.find_element_by_class_name('dialog-content')
        dates_list = dates_to_choose.find_elements_by_class_name('button')
        for elem in dates_list:
            if date == elem.get_property("innerText"):
                self.click_button(elem)
                break
        try:
            available_slots_parent = self.driver.find_element_by_xpath('//*[@id="doorPolicyForm"]/div[3]')
            slots = available_slots_parent.find_elements_by_class_name('time-slot')
            if len(slots) == 0:
                return
            slots.sort(key=sort_key, reverse=True)
            self.click_button(slots[0])
            yes_button = self.driver.find_element_by_id('dialog_book_yes')
            self.click_button(yes_button)
            print("Successfully booked something")
        except NoSuchElementException as ex:
            print("No available slots")

    def quit(self):
        print("Quitting")
        self.driver.quit()

def main():
    setup()
    f = FitDriver()
    f.login()
    if f.check_for_date_select():
        pass
    else:
        f.quit()

if __name__ == '__main__':
    main()