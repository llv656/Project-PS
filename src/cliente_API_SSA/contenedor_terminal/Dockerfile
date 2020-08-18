FROM tsl0922/ttyd

RUN apt-get -y update \
    && apt-get install -y openssh-client \
    && apt-get -y clean

ENV USER=""
ENV PASS=""
ENV PATH_CERT=""
ENV PATH_KEY=""
ENV URL_TERMINAL=""

COPY ./start.sh /
RUN mkdir /certs
RUN chmod 700 /start.sh

RUN useradd -s /bin/bash limitado
RUN chown limitado ./start.sh
CMD /start.sh
