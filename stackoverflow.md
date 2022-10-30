I'm just starting with AWS Lambda functions (and serverless deployment in general), migrating from Heroku as their free tier won't be available soon. It is a FAST API project, using python 3.9, MongoDB (connecting to a ATLAS Cluster) and selenium+chrome+chromedriver for a simple web scraping route.

I've decided to go straight with the container image deployment option, as with it I should be able to test everything locally and reduce the debugging after pushing it to production. For most of the part, setting up the routes following the documentation and online sources went pretty smooth. With the local Docker logging and terminal access to the container, I've been able to debug, deploy ad test the routes, including database connections, and the behaviour locally was exactly as the behaviour after deployment.

The problem showed up on the web scraping part of it, especially with google chrome and chromedriver.
Setting it up locally, with local environment meaning building and running the **_container_** locally, using the suggested lambda image from AWS Public Gallery `public.ecr.aws/lambda/python:3.9` wasn't so hard either. I've simplified the project and isolated just the dockerfile and the driver setup in a [this repository](https://github.com/richardnm-2/fastapi_aws), with a branch working fine both locally and deployes, and another working only locally. The fully working

## Local working setup, but not working deployed

dockerfile

```docker
FROM public.ecr.aws/lambda/python:3.9

# this actually is the second locally working attempt, the first one consisted in having the chromedriver linux binary copied directly from the source folder, which lead to a permission error when deployed
RUN yum install -y unzip && \
    curl -Lo "/tmp/chromedriver.zip" "https://chromedriver.storage.googleapis.com/107.0.5304.62/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /opt/

RUN yum install -y https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome-stable-107.0.5304.68-1.x86_64.rpm

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt

COPY app.py ./
CMD [ "app.handler" ]
```

selenium driver setup - same as I had working in Heroku

```python
    CHROMEDRIVER_PATH = '/opt/chromedriver'
    CHROME_BIN = '/opt/google/chrome/chrome'

    options = webdriver.ChromeOptions()

    options.binary_location = CHROME_BIN

    options.add_argument('--no-sandbox')
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-gpu')
    options.add_argument("window-size=1400,800")

    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, chrome_options=options)
```

I wouldn't have a working setup without [umihico's docker-selenium-lambda repo](https://github.com/umihico/docker-selenium-lambda), which uses chrome-linux from a different source than the one I first used locally, needs a lot of other packages

## Umihico's dockerfile setup

```docker
FROM public.ecr.aws/lambda/python:3.9 as build

RUN yum install -y unzip && \
    curl -Lo "/tmp/chromedriver.zip" "https://chromedriver.storage.googleapis.com/107.0.5304.62/chromedriver_linux64.zip" && \
    curl -Lo "/tmp/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1047731%2Fchrome-linux.zip?alt=media" && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    unzip /tmp/chrome-linux.zip -d /opt/

FROM public.ecr.aws/lambda/python:3.9

RUN yum install xz atk cups-libs gtk3 libXcomposite alsa-lib tar \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel unzip bzip2 -y -q

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt

COPY --from=build /opt/chrome-linux /opt/chrome
COPY --from=build /opt/chromedriver /opt/

COPY app.py ./
CMD [ "app.handler" ]
```
I only changed the repository image with the default recommended one, and it worked perfectly. I even tested without the build part, changing then the path of the binaries (exluding the FROM ... as build, pulling only once from public.ecr), and everything still worked after deployment.

also, the driver setup changed, to:
```python
    options = webdriver.ChromeOptions()

    options.binary_location = CHROME_BIN

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

    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, chrome_options=options)
```

using my original driver setup would make even the chrome-linux from umihico throw an Exception, not beeing able to discover an open window in chrome

After experimenting with all these options, even though it works, I have two questions, and I would really appreciate any help with it:

1. How do I get my local environment to behave as the live one? Regarding not only to chrome capability to start, but also read-only paths, as I commented [here](https://stackoverflow.com/questions/65429877/aws-lambda-container-running-selenium-with-headless-chrome-works-locally-but-not) and [here]()

2. I'm also not completly familiar with Docker, an might be missing out on something big here, but isn't the whole point in making container images to be able to run them regardless of the environment that they're on?