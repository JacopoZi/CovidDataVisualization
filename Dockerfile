FROM python:3.7-alpine
RUN mkdir -p /scripts
WORKDIR /scripts
COPY ./scripts /scripts
RUN pip install -r requirements.txt
CMD ["python3", "ExportData.py"]