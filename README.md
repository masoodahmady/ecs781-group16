# ecs781-group16

## Table of Contents
* [Introduction](#introduction)
* [Instructions](#instructions)

## Introduction
This is the GitHub repository for the coursework of ECS781 Cloud Computing for group 16, in the Spring Semester of 2021.

It is a fictional cryptocurrency portfolio tracker built using Flask and SQLAlchemy.

### Third-party libraries and APIs used
This coursework makes use of the following libraries and APIs.

#### API
* [CoinGecko API](https://www.coingecko.com/en/api)

#### Libraries
* [pycoingecko](https://github.com/man-c/pycoingecko)
* [Flask](https://flask.palletsprojects.com/)
* [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
* [PyMySQL](https://github.com/PyMySQL/PyMySQL)


## Instructions
### Requirements
The following environment should be set at the host.

This is definitely not the best practice to save a database password. But due to limited time, and considering it is a non-production application, this is not as bad as doing the same in a production environment.
```bash
export SQLALCHEMY_DATABASE_USERNAME=<MySQL database username>
export SQLALCHEMY_DATABASE_PASSWORD=<MySQL database password>
export SQLALCHEMY_DATABASE=<MySQL database name>
export SQLALCHEMY_DATABASE_URI_HOST=<MySQL database hostname>
```

### Running the Application Locally
* To install the required Python libraries:
```bash
cd app
pip3 install -r requirements.txt
```

* To run the application locally:
```bash
cd app
python3 app.py
```

### Build and Run the Application on Docker
* To create a docker image
```bash
cd app
docker build . --tag=ecs781group16:<version>
```

* To run the application on Docker
```bash
docker run -p <host port>:5000 \
--env SQLALCHEMY_DATABASE_USERNAME \
--env SQLALCHEMY_DATABASE_PASSWORD \
--env SQLALCHEMY_DATABASE \
--env SQLALCHEMY_DATABASE_URI_HOST \
ecs781group16:<version>
```