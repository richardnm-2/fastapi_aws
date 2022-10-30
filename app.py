from selenium import webdriver
from fastapi import FastAPI
from mangum import Mangum
from tempfile import mkdtemp

app = FastAPI()
handler = Mangum(app)

CHROMEDRIVER_PATH = '/opt/chromedriver'
CHROME_BIN = '/opt/google/chrome/chrome'


def get_driver():
    options = webdriver.ChromeOptions()

    options.binary_location = CHROME_BIN

    '''
    lambda: selenium.common.exceptions.WebDriverException: Message: unknown error: unable to discover open window in chrome
    locally: works fine
    '''
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    '''chrome crashes right from start on lambda, works fine locally'''
    # options.add_argument('--no-sandbox')
    # options.add_argument("--headless")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument('--disable-gpu')
    # options.add_argument("window-size=1400,800")

    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, chrome_options=options)

    return driver


@app.get("/chromedriver")
async def chromedriver():
    print('locally tested - OK')
    print('ENTERED ENDPOINT /chromedriver')
    driver = get_driver()
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")

    return {"title": driver.title}


@app.get("/no_chromedriver")
async def no_chromedriver():
    print('ENTERED ENDPOINT /no_chromedriver')

    return {"title": 'NO_CHROMEDRIVER'}
