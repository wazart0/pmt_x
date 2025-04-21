FROM node:21.6.2-bookworm


RUN apt-get update && apt-get install -y openssh-server 
RUN sed -i 's/.*PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/.*PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN echo "root:dev" | chpasswd

WORKDIR /app

# RUN apk add --no-cache npm

# RUN npm install -g nodemon 
# RUN npm install gantt rsuite --save



# COPY requirements_dev.txt .

# RUN pip install -r requirements_dev.txt

