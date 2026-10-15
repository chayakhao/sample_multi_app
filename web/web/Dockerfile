FROM python:3.12-slim
WORKDIR /home/myapp
COPY ./requirements.txt /home/myapp/
RUN pip install --no-cache-dir -r requirements.txt
COPY ./templates/ /home/myapp/templates/
COPY ./static/ /home/myapp/static/
COPY ./app.py /home/myapp/
CMD ["python3", "/home/myapp/app.py"]
EXPOSE 8080
