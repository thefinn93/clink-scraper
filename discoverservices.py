#!/usr/bin/env python3
"""Usage:

 osmfilter newplace.osm --keep="addr:housenumber and addr:street" --drop-relations --drop-ways |\
 osmconvert - --all-to-nodes --csv="addr:housenumber addr:street addr:city addr:postcode @id @lat @lon" |\
 ./discoverservices.py
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import dataset
import sys
import csv

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)


def class_exists(driver, c):
    try:
        driver.find_element_by_class_name(c)
        return True
    except NoSuchElementException:
        return False


def get_max_speed(driver):
    try:
        return driver.find_element_by_id("highestSpeedWL").find_element_by_class_name('strongText').text
    except NoSuchElementException:
        return None


def check_mdu(driver):
    try:
        driver.find_element_by_class_name('mduOptions').find_element_by_name('addressid').click()
        driver.find_element_by_id('submitSecUnit').click()
        return True
    except NoSuchElementException:
        return False


def dialup_only(driver):
    try:
        driver.find_element_by_class_name('dialupOnly')
        return True
    except NoSuchElementException:
        return False


def open_address_modal(driver):
    try:
        driver.find_element_by_class_name("btn-check-avail").click()
    except NoSuchElementException:
        driver.find_element_by_id("home-internet-speed-check").click()


def check_address(driver, address):
    logger.info("Checking CLink speeds at %s", address)
    if class_exists(driver, "btn-check-avail"):
        logger.info("Searching for another address, waiting for btn-check-avail to become clickable...")
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-check-avail')))
        logger.info("Clicking!")
        element.click()
    else:
        driver.find_element_by_id("home-internet-speed-check").click()
    address_box = driver.find_element_by_id("ctam_nc-sfaddress")
    if not address_box.is_displayed():
        logger.info("Address box not visible! Refreshing...")
        driver.refresh()
        return check_address(driver, address)
    address_box.send_keys(address, Keys.RETURN)
    max_speed = get_max_speed(driver)
    if check_mdu(driver):
        max_speed = get_max_speed(driver)
    if max_speed is None and not dialup_only(driver):
        logger.warning("max speed at %s none, but not cuz it's dialup only! that's weird", address)
    return max_speed


if __name__ == "__main__":
    csvreader = csv.reader(sys.stdin, delimiter='\t')
    db = dataset.connect("sqlite:///clink.db")
    table = db['addresses']
    for a in csvreader:
        housenum = a[0]
        unit = None
        if " " in a[0]:
            housenum, unit = a[0].split(" ", 2)
        address = "{} {}, {} WA {}".format(housenum, a[1], a[2], a[3])
        if table.find_one(address=address) is None and len(a[1]) > 0:
            driver = webdriver.Chrome()
            driver.get("http://www.centurylink.com/home/internet/")
            speed = check_address(driver, address)
            driver.close()
            logger.info("%s\t%s", address, speed)
            table.insert(dict(address=address, speed=speed, osm_id=a[4], lat=a[5], lon=a[6]))
            db.commit()
        else:
            logger.info("Skipping %s, already in DB" % address)
