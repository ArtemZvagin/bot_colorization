FROM python:3.10
WORKDIR /app
COPY config.py main.py requirements.txt ./ 
RUN pip --no-cache-dir install -r requirements.txt
CMD ["python", "main.py"]