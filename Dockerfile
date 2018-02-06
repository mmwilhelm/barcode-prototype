FROM ubuntu:latest
WORKDIR /app
COPY . /app
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential 
RUN pip install --upgrade pip
RUN pip install setuptools --upgrade
RUN apt-get install -y python-pip libzbar0 libzbar-dev
RUN pip install -r requirements.txt
EXPOSE 80
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=80"]
