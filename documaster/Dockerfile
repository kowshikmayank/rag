FROM python:3.10
# Stream w/o buffer, so in event of a crash we do not lose logs present in the buffer but not written out
ENV PYTHONUNBUFFERED=TRUE

RUN apt-get -y update && apt-get install -y --no-install-recommends build-essential\
    nginx \
    ca-certificates \
    jq \
    awscli \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /opt/documaster/requirements.txt
RUN pip3 install -r /opt/documaster/requirements.txt

COPY ./documaster/ /opt/documaster/

ENV PATH="$PATH:/opt/documaster"
WORKDIR /opt/documaster
RUN chmod +x /opt/documaster/serve
EXPOSE 8080
CMD ["/opt/documaster/serve"]

