#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive
echo "deb http://ftp5.gwdg.de/pub/linux/debian/debian/ wheezy main contrib non-free" > /etc/apt/sources.list
echo "deb-src http://ftp5.gwdg.de/pub/linux/debian/debian/ wheezy main contrib non-free" >> /etc/apt/sources.list
echo "deb http://security.debian.org/ wheezy/updates main" >> /etc/apt/sources.list
echo "deb-src http://security.debian.org/ wheezy/updates main" >> /etc/apt/sources.list

apt-get update
apt-get -y upgrade

ln -vsf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

apt-get -y install apache2-mpm-prefork libapache2-mod-php5 mysql-server phpmyadmin python3 python3-pip
cd /vagrant && pip-3.2 install -r requirements.txt
mysqladmin -uroot create parselog

echo "+-------------------------------------------------+"
echo "| Use http://127.0.0.1:8084/ to view the database |"
echo "|   Username: root                                |"
echo "|                                                 |"
echo "| To add a log file:                              |"
echo "|   vagrant ssh                                   |"
echo "|   cd /vagrant                                   |"
echo "|   ./parselog <logfile>                          |"
echo "+-------------------------------------------------+"