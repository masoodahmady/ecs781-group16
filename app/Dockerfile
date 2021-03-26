FROM python:3.8.8-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 80
EXPOSE 443
EXPOSE 5000
CMD [ "python", "app.py" ]
