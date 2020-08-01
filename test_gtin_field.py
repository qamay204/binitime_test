import time
from seleniumwire import webdriver as sw
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
# import requests
import unittest


def wait_until_element_is_visible(driver, selector, seconds=10):
    WebDriverWait(driver, seconds).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
    )


def login_into_app(driver, auth_data):
    wait_until_element_is_visible(driver, '#loginform-username')
    driver.find_element(By.CSS_SELECTOR, '#loginform-username').send_keys(auth_data[0])
    driver.find_element(By.CSS_SELECTOR, '#loginform-password').send_keys(auth_data[1])
    wait_until_element_is_visible(driver, '[name="login-button"]')
    driver.find_element(By.CSS_SELECTOR, '[name="login-button"]').click()


def gtni_invalid(driver):
    try:
        driver.find_element_by_xpath('//p[contains(., "GTIN (EAN/UPC) is not valid")]')
        return True
    except exceptions.NoSuchElementException as e:
        return False


def gtni_correct(driver):
    try:
        gtni_ctx = driver.find_element_by_xpath('//div[./input[contains(@id, ("productform-ean"))]]')
        cl = gtni_ctx.get_attribute("class")
        if 'has-danger' in cl:
            return False
        else:
            return True
    except exceptions.NoSuchElementException as e:
        return True


def gtni_invalid_12_14(driver):
    try:
        driver.find_element_by_xpath('//p[contains(., "GTIN (EAN/UPC) must contain exactly 13 digits.")]')
        return True
    except exceptions.NoSuchElementException as e:
        return False


class TestBasicLevel(unittest.TestCase):
    TEST_DATA = {
        'url': 'http://gepard.bintime.com/login',
        'basic_auth': ['admin', 'skdf$#&&%tg'],
        'bo_auth': ['test-qa', 'test-qa'],
        'thirteen_digits_code': 1234567890123,
    }

    def setUp(self):
        # self.driver = webdriver.Chrome()
        # self.driver.implicitly_wait(1)
        # self.driver.set_window_size(1920, 1080)
        # res = requests.get('http://gepard.bintime.com/login',
        #                    headers={'Authorization': 'Basic YWRtaW46c2tkZiQjJiYldGc='})
        self.driver = sw.Chrome()

    def tearDown(self) -> None:
        self.driver.quit()
        time.sleep(0.5)

    def reach_test_elem(self):
        driver = self.driver
        driver.implicitly_wait(3)
        driver.header_overrides = {'Authorization': 'Basic YWRtaW46c2tkZiQjJiYldGc='}
        driver.get(self.TEST_DATA['url'])
        login_into_app(driver, self.TEST_DATA['bo_auth'])
        driver.find_element(By.XPATH, '//a[contains(., "Products")]').click()
        driver.find_elements_by_xpath('//a[contains(., "Products")]  ')[1].click()
        driver.find_element_by_xpath('//a[contains(., "Create product")]').click()
        return driver

    def test_positive_valid_gtni(self):
        driver = self.reach_test_elem()
        wait_until_element_is_visible(driver, '#productform-ean')
        driver.find_element_by_css_selector('#productform-ean').send_keys('9878987654568', Keys.ENTER)
        self.assertTrue(gtni_correct(driver))

    def test_negative_invalid_gtni(self):
        driver = self.reach_test_elem()
        wait_until_element_is_visible(driver, '#productform-ean')
        driver.find_element_by_css_selector('#productform-ean').send_keys('1234567890123', Keys.ENTER)
        self.assertTrue(gtni_invalid(driver))

    def test_negative_gtni12(self):
        driver = self.reach_test_elem()
        wait_until_element_is_visible(driver, '#productform-ean')
        driver.find_element_by_css_selector('#productform-ean').send_keys('98789876545611', Keys.ENTER)
        self.assertTrue(gtni_invalid_12_14(driver))

    def test_negative_gtni14(self):
        driver = self.reach_test_elem()
        wait_until_element_is_visible(driver, '#productform-ean')
        driver.find_element_by_css_selector('#productform-ean').send_keys('987898765450', Keys.ENTER)
        self.assertTrue(gtni_invalid_12_14(driver))


if __name__ == '__main__':
    unittest.main()
