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

The fully working setup would not be possible without [umihico's repo](https://github.com/umihico/docker-selenium-lambda)
