FROM python:3.7

RUN mkdir /dependencias

COPY requeriments.txt /dependencias

RUN pip3 install -r /dependencias/requeriments.txt

ENV SECRET_KEY_BE=""
ENV PATH_LOGS_BE=""
ENV NAME_BD_BE=""
ENV USR_BD_BE="" 
ENV PASS_DB_BE=""
ENV HOSTDJ_BE=""
ENV DB_AS="" 
ENV PORTDJ_BE="" 
ENV USR_CLIENT_SERVICE_BE=""
ENV PASS_CLIENT_SERVICE_BE=""
ENV URL_CLIENT_SERVICE_BE=""
ENV MASTER_USR_BE=""
ENV MASTER_PASS_BE=""

RUN mkdir /code
RUN mkdir /LOGS_BACK_END
RUN mkdir /start

COPY ./start.sh /start
RUN chmod 751 /start/start.sh
RUN chmod 740 /LOGS_BACK_END

WORKDIR /code

RUN useradd -s /bin/bash limitado

RUN chown -R limitado /code
RUN chown -R limitado /LOGS_BACK_END

CMD /start/start.sh

