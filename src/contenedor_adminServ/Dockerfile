FROM python:3.7

RUN mkdir /dependencias

COPY requeriments.txt /dependencias

RUN pip3 install -r /dependencias/requeriments.txt

ENV SECRET_KEY=""
ENV PATH_LOGS=""
ENV TOKEN_TELEGRAM=""
ENV NAME_BD=""
ENV CHAT_ID=""
ENV USR_BD=""
ENV PASS_BD=""
ENV DB_uno=""
ENV DB_dos=""
ENV SECRET_USRM=""
ENV SECRET_PASSM=""
ENV PORTDJ=""
ENV HOSTDJ=""
ENV PATH_ALERTA=""
ENV SECRET_USR_SERVICE=""
ENV SECRET_PASS_SERVICE=""
ENV SECRET_URL_SERVICE=""

RUN mkdir /code
RUN mkdir /path_plugins
RUN mkdir /LOGS_FRONT_END
RUN mkdir /start

COPY ./start.sh /start
RUN chmod 751 /start/start.sh

WORKDIR /code

RUN useradd -s /bin/bash limitado

RUN chown -R limitado /code
RUN chown -R limitado /path_plugins
RUN chown -R limitado /LOGS_FRONT_END

CMD /start/start.sh
