# 1) choose base container
# generally use the most recent tag

# data science notebook
# https://hub.docker.com/repository/docker/ucsdets/datascience-notebook/tags
ARG BASE_CONTAINER=ucsdets/datascience-notebook:2020.2-stable

# scipy/machine learning (tensorflow)
# https://hub.docker.com/repository/docker/ucsdets/scipy-ml-notebook/tags
# ARG BASE_CONTAINER=ucsdets/scipy-ml-notebook:2020.2-stable

FROM $BASE_CONTAINER

LABEL maintainer="UC San Diego ITS/ETS <ets-consult@ucsd.edu>"

# 2) change to root to install packages
USER root

RUN	apt-get update && \
    apt-get -y upgrade && \
    apt-get install htop -y && \
	apt-get install aria2 -y && \
	apt-get install traceroute -y && \
	pip install --upgrade pip && \
	pip install geopandas && \
	pip install babypandas && \
    pip install pandas && \
    pip install numpy && \
    pip install matplotlib && \
    conda install decorator && \
    pip install networkx && \
    pip install stellargraph && \
    pip install sklearn && \
    pip install gensim && \
    pip install nbconvert && \
    pip install decorator
        
    

# 3) install packages
ENV APK_SCRIPT https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool
ENV APK_JAR https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.4.1.jar

RUN mkdir -p /usr/local/bin

RUN P=/tmp/$(basename $APK_SCRIPT) && \
    wget -q -O $P $APK_SCRIPT && \
    chmod +x $P && \
    mv $P /usr/local/bin

RUN P=/tmp/$(basename $APK_JAR) && \
    wget -q -O $P $APK_JAR && \
    chmod +x $P && \
    mv $P /usr/local/bin/apktool.jar

RUN pip install --no-cache-dir networkx scipy python-louvain

RUN conda  clean -tipy

# 4) change back to notebook user

COPY /run_jupyter.sh /
RUN chmod 755 /run_jupyter.sh
USER $NBUID

# Override command to disable running jupyter notebook at launch
# CMD ["/bin/bash"]