FROM python:3.8.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /alert
COPY requirements.txt /alert
RUN pip install -r /alert/requirements.txt --no-cache-dir
COPY alert.py /alert
WORKDIR /alert
CMD ["python", "alert.py"]
