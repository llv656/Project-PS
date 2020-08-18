FROM python:3.7

RUN mkdir /dependencias

COPY requeriments.txt /dependencias

RUN pip3 install -r /dependencias/requeriments.txt

ENV SECRET_KEY=""
ENV PATH_LOGS=""
ENV PATH_KEY=""
ENV PATH_CERT=""
ENV USER=""
ENV PASS=""
ENV NAME_BD=""
ENV USR_BD=""
ENV PASS_BD=""
ENV PORTDJ=""
ENV HOSTDJ=""
ENV USR_MASTER_SERVICE=""
ENV PASS_MASTER_SERVICE=""
ENV URL_TERMINAL=""
ENV USR_TERMINAL=""
ENV PASS_TERMINAL=""

RUN mkdir /code
RUN mkdir /LOGS_CLIENTE
RUN mkdir /start

COPY ./start.sh /start
RUN chmod 751 /start/start.sh
RUN chmod 740 /LOGS_CLIENTE

WORKDIR /code

RUN useradd -s /bin/bash limitado

RUN chown -R limitado /code
RUN chown -R limitado /LOGS_CLIENTE

CMD /start/start.sh
