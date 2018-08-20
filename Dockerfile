FROM gilureta/opengl:ubuntu16.04

WORKDIR /setup
COPY requirements.txt /setup/

ENV PYTHONIOENCODING=utf-8

RUN apt-get update && apt-get install -y \
    x-window-system \
    build-essential \
    cmake \
    wget \
    g++-4.8 \
    freeglut3-dev \
    libblas-dev \
    liblapack-dev \
    libglu1-mesa-dev \
    xorg-dev \
    python3 \
    python3-pip

# make python3 the default
RUN cd /usr/local/bin \
    && ln -s `which pydoc3` pydoc \
    && ln -s `which python3` python \
    && ln -s `which python3-config` python-config \
    && ln -fs `which pip3` pip

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# run.sh
COPY run.sh /setup/
