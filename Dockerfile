FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.1.0+cpu torchvision==0.16.0+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV CUDA_VISIBLE_DEVICES=""

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]