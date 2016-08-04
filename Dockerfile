FROM python:2.7-alpine

COPY ./spark-ui-proxy.py /

EXPOSE 80

ENTRYPOINT ["python", "/spark-ui-proxy.py"]
