FROM gabrielfalcao/cook-my-list-base

VOLUME /cookmylist.com

ENV PYTHONPATH /app/
ENV UPLOAD_FOLDER /cookmylist.com/file-uploads
ENV PIP_CACHE_DIR /pip/cache

COPY . /app/
RUN /venv/bin/pip install /app

RUN cookmylist-scraper check || true
ENV SCRAPER_ENGINE_PORT 5000
ENV SCRAPER_ENGINE_VERSION 4

EXPOSE 5000
EXPOSE 4242
EXPOSE 6969


CMD scraper-engine web "--port=$SCRAPER_ENGINE_PORT"
