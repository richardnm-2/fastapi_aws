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