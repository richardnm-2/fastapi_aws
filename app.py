from selenium import webdriver
from fastapi import FastAPI
from mangum import Mangum
from tempfile import mkdtemp

app = FastAPI()
handler = Mangum(app)

CHROMEDRIVER_PATH = '/opt/chromedriver'
CHROME_BIN = '/opt/chrome/chrome'


def get_driver():
    options = webdriver.ChromeOptions()

    options.binary_location = CHROME_BIN

    options.add_argument('--no-sandbox')
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-gpu')
    options.add_argument("window-size=1400,800")

    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, chrome_options=options)

    return driver


@app.get("/chromedriver")
async def chromedriver():
    print('ENTERED ENDPOINT /chromedriver')
    driver = get_driver()
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")

    return {"title": driver.title}


@app.get("/no_chromedriver")
async def no_chromedriver():
    print('ENTERED ENDPOINT /no_chromedriver')

    return {"title": 'NO_CHROMEDRIVER'}
