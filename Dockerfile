FROM python:3.7.3-slim-stretch

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -y update && apt-get install -y \
    procps \
    curl \
    unzip \
    vim \
    nano \
    netcat \
    libreadline7 \
    libgdbm3 \
    libexpat1 \
    net-tools \
    git \
    ca-certificates

RUN apt-get -y update && apt-get install -y \
    libpcre3-dev \
    zlib1g-dev \
    libssl-dev \
    libreadline-dev \
    libncursesw5-dev \
    libncurses5-dev \
    libffi-dev \
    libbz2-dev \
    liblzma-dev \
    libexpat1-dev \
    libgdbm-dev \
    tcl-dev \
    tk-dev \
    gnupg \
    dirmngr \
    dnsutils \
    dh-autoreconf \
    build-essential

RUN curl -L -o /tmp/nginx.tar.gz https://nginx.org/download/nginx-1.16.0.tar.gz \
        && tar -zxf /tmp/nginx.tar.gz -C /tmp/ \
        && mv /tmp/nginx-1.16.0 /tmp/nginx \
        && cd /tmp/nginx \
        && sed -i 's/Server: nginx/Server: require.id/' src/http/ngx_http_header_filter_module.c \
        && ./configure --with-http_ssl_module --with-http_v2_module --with-http_realip_module \
        && make \
        && make install \
        && rm -rf /tmp/nginx /tmp/nginx.tar.gz \
        && adduser --disabled-login --shell /bin/true nginx \
        && mkdir -p /run/nginx \
        && chown nginx:nginx /run/nginx

RUN curl -L -o /tmp/get-poetry.py https://raw.githubusercontent.com/sdispater/poetry/0.12.16/get-poetry.py \
    && python /tmp/get-poetry.py --yes --version 0.12.16 \
    && rm -f /tmp/get-poetry.py \
    && mv /root/.poetry /usr/local/lib/poetry \
    && (echo 'python /usr/local/lib/poetry/bin/poetry "$@"' > /usr/local/bin/poetry) \
    && chmod +x /usr/local/bin/poetry \
    && ln -s /usr/local/bin/poetry /usr/bin/poetry \
    && poetry config settings.virtualenvs.create 0

ADD utils/nginx/nginx.conf /usr/local/nginx/conf/nginx.conf
ADD utils/init.d/nginx /etc/init.d/nginx
ADD utils/dotfiles/bashrc /root/.bashrc
ADD utils/dotfiles/vimrc /etc/vim/vimrc
ADD utils/dotfiles/vimrc /root/.vimrc
ADD utils/bin/start-service /bin/start-service
RUN chmod +x /etc/init.d/nginx /bin/start-service

RUN service nginx start
RUN rm -f /run/nginx.pid
EXPOSE 80

RUN mkdir -p /root/.ssh
RUN (host=github.com; ssh-keyscan -H $host; for ip in $(dig @1.1.1.1 github.com +short); do ssh-keyscan -H $host,$ip; ssh-keyscan -H $ip; done) 2> /dev/null >> /root/.ssh/known_hosts

ENTRYPOINT ["/bin/start-service"]

WORKDIR /
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

ADD app /app
WORKDIR /app
ENV PYTHONPATH=src

CMD tomodachi run src/service/app.py
