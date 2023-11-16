FROM python:3.11

# Set the working directory in the container
WORKDIR /main

COPY . .

RUN apt-get update && apt-get install -y libgl1-mesa-glx


RUN pip3 install torch

# Install dependencies
RUN pip install -r requirements.txt


