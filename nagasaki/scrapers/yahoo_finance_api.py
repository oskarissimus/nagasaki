from sys import platform
from selenium import webdriver
import selenium
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path


class element_inner_html_len_is_greater_than(object):
    """An expectation for checking that length of inner html of element is greater than the given length.

    locator - used to find the element
    returns the WebElement once its inner html length is greater than the particular length
    """

    def __init__(self, locator, len):
        self.locator = locator
        self.len = len

    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Finding the referenced element
        if len(element.get_attribute("innerHTML")) > self.len:
            return element
        else:
            return False


def scrape_api_key(email, password):
    email_input_xpath = "/html/body/div/div/main/div[1]/div/div/div/div[2]/div/div/form/div/fieldset/div[1]/div/div/input"
    password_input_xpath = "/html/body/div/div/main/div[1]/div/div/div/div[2]/div/div/form/div/fieldset/div[2]/div/div[1]/input"
    login_button_xpath = (
        "/html/body/div/div/main/div[1]/div/div/div/div[2]/div/div/form/div/button"
    )
    api_key_element_xpath = "/html/body/div/div/main/div[1]/div[1]/div[1]"
    yahoo_finance_api_url = "https://www.yahoofinanceapi.com/dashboard"
    options = Options()
    options.headless = True

    if platform == "linux" or platform == "linux2":
        executable_path = (
            Path(__file__).parent.resolve()
            / "drivers"
            / "geckodriver-v0.31.0-linux64"
            / "geckodriver"
        )
    elif platform == "darwin":
        executable_path = (
            Path(__file__).parent.resolve()
            / "drivers"
            / "geckodriver-v0.31.0-macos"
            / "geckodriver"
        )
    else:
        raise YahooFinanceScrapperException(f"Platform {platform} not " f"supported")

    service = FirefoxService(executable_path=executable_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(yahoo_finance_api_url)
    email_input = driver.find_element(by="xpath", value=email_input_xpath)
    email_input.send_keys(email)
    password_element = driver.find_element(by="xpath", value=password_input_xpath)
    password_element.send_keys(password)
    login_button = driver.find_element(by="xpath", value=login_button_xpath)
    login_button.click()
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.XPATH, api_key_element_xpath), "API key")
    )
    inner_html_len_before_key_is_loaded = len("<b>API key</b>: ")
    locator = (By.XPATH, api_key_element_xpath)
    element = WebDriverWait(driver, 10).until(
        element_inner_html_len_is_greater_than(
            locator, inner_html_len_before_key_is_loaded
        )
    )

    return element.get_attribute("innerHTML")[-40:]


class YahooFinanceScrapperException(Exception):
    pass
