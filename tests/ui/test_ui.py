from flask import url_for
from selenium import webdriver
import os

from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')


def test_case1(live_server):
    driver = webdriver.Chrome(executable_path=os.path.join(os.environ.get('CHROMEWEBDRIVER'),"chromedriver"), options=options)
    driver.get(url_for('main.home', _external=True))
    print(url_for('main.home', _external=True))
    print("Title of the webpage is {}".format(driver.title))
    assert 'Capital Gain Loss Calculator' == driver.title
    driver.quit()
