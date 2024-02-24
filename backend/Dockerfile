FROM python:3-bookworm

RUN apt-get update && apt-get install -y openssh-server
RUN sed -i 's/.*PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/.*PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN echo "root:dev" | chpasswd

COPY requirements_dev.txt /app/requirements_dev.txt
RUN pip3 install -r /app/requirements_dev.txt

WORKDIR /app
