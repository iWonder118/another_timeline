FROM public.ecr.aws/lambda/python:3.8

# install build libs
RUN yum groupinstall -y "Development Tools" \
    && yum install -y which openssl

# install mecab
WORKDIR /tmp
RUN  curl -L "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7cENtOXlicTFaRUE" -o mecab-0.996.tar.gz \
    && tar xzf mecab-0.996.tar.gz \
    && cd mecab-0.996 \
    && ./configure --build=arm\
    && make \
    && make check \
    && make install \
    && cd .. \
    && rm -rf mecab-0.996*


# setup python
COPY ./requirements.txt /opt/
RUN pip install --upgrade pip && pip install -r /opt/requirements.txt

# set function code
WORKDIR /var/task
COPY app.py .
COPY ./get_tw_hz/result/tw_hz_no_lf.csv .
CMD ["app.generate_tw_hz"]