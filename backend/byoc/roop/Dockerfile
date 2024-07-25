# Base image
ARG ECR_REGISTRY
ARG ECR_REPOSITORY
ARG IMAGE_TAG
FROM ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}

# Install necessary packages
RUN apt-get update && \
    apt-get install -y sudo wget git xz-utils nginx ca-certificates libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && \
    pip install opencv-python-headless opencv-contrib-python flask gevent gunicorn boto3 && \
    rm -rf /root/.cache

# Clone the roop repository to the home directory and install requirements
RUN mkdir -p /opt/program/roop && \
    git clone https://github.com/s0md3v/roop /opt/program/roop && \
    cd /opt/program/roop && \
    pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

COPY src /opt/program
WORKDIR /opt/program

RUN chmod +x /opt/program/serve

EXPOSE 8080

ENTRYPOINT ["serve"]