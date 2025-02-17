FROM ubuntu
RUN apt-get update && apt-get install -y nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log
RUN rm -rf /etc/nginx/sites-enabled/default
RUN rm -rf /etc/nginx/sites-available/default

COPY /deploy/nginx/nginx.conf  /etc/nginx/sites-enabled/server
COPY /deploy/nginx/nginx.conf  /etc/nginx/sites-available/server

COPY /static/ /app/static/

CMD ["nginx", "-g", "daemon off;"]
EXPOSE 80 443