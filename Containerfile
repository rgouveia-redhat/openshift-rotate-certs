FROM registry.access.redhat.com/ubi8/python-38

RUN pip3 install Kubernetes

USER default

WORKDIR /app
COPY ./rotate-certs.py /app

CMD ["python", "/app/rotate-certs.py"]

