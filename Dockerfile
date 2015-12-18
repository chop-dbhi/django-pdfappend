FROM python:3.4.3-wheezy

MAINTAINER Jeff Miller "millerjm1@email.chop.edu"

RUN apt-get update -qq --fix-missing
RUN apt-get install software-properties-common -y
RUN apt-get install -y\
    build-essential\
    git-core\
    libldap2-dev\
    libpq-dev\
    libsasl2-dev\
    libssl-dev\
    libxml2-dev\
    libxslt1-dev\
    libffi-dev\
    openssl\
    wget\
    zlib1g-dev

RUN pip install Django
RUN pip install uwsgi
RUN pip install requests_futures
RUN pip install elasticsearch
RUN pip install git+https://github.com/mstamy2/PyPDF2.git

ADD . /opt/app

ENV APP_NAME PDFAPPEND

CMD ["/opt/app/scripts/nginx.sh"]

EXPOSE 8000