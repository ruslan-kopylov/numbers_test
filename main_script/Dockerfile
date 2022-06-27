FROM python:3.8.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /script
COPY requirements.txt /script
RUN pip install -r /script/requirements.txt --no-cache-dir
COPY get_data.py /script
COPY credentials.json /script
WORKDIR /script
CMD ["python", "get_data.py"]
