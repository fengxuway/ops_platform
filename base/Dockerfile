FROM reg.xiaoneng.cn/library/python:3.5

MAINTAINER fengxu <fengxu@xiaoneng.cn>

COPY id_rsa /root/.ssh/
COPY id_dsa /root/.ssh/
COPY ssh_config /etc/ssh/
COPY pip.conf /root/.pip/
COPY sources.list /etc/apt/
COPY get-pip.py /tmp/

RUN apt -y update \
    && apt -y install nginx \
    && apt -y install sshpass \
    && pip install --upgrade pip \
    && rm -rf /etc/nginx/sites-enabled/default \
    && rm -rf /var/lib/apt/lists/* \
    && /usr/bin/python /tmp/get-pip.py \
    && pip2 install supervisor \
    && mkdir -p /data/log/supervisor

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt \
    && rm -rf /tmp/* \
    && chmod 600 /root/.ssh/id_*p

COPY supervisord.conf /etc/
COPY nginx.ini /etc/supervisor.d/

EXPOSE 80

COPY docker-entrypoint.sh /

VOLUME ["/data"]

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["supervisord", "-n", "-c", "/etc/supervisord.conf"]
