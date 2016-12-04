#!/bin/bash

set -e

MYSQL_PASS="root"

DEBIAN_FRONTEND=noninteractive

# silently (-y) install mysql-server and set the value of MYSQL_PASS as the password
# mysql-server is a prerequisite for slingshot
echo "mysql-server mysql-server/root_password password $MYSQL_PASS" | sudo debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $MYSQL_PASS" | sudo debconf-set-selections
sudo apt-get install -y mysql-server

# silently install other prerequisites for slingshot
sudo apt-get install -y openssh-server build-essential git-core \
	python-mysqldb libmysqlclient15-dev python-dev libxml2-dev \
	libxslt1-dev curl libbz2-dev libsqlite3-dev libgdbm-dev \
	libssl-dev libexpat1-dev libncurses5-dev qemu-system

# install pyenv's prerequisites (those not in common with slingshot only)
sudo apt-get install -y zlib1g-dev libreadline-dev wget llvm libncursesw5-dev

# install pyenv and update the environment
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# install virtual python env
pyenv install 2.7.10

# clone slingshot and install it
git clone https://github.com/salpha2004/slingshot.git
cd slingshot
python ./setup.py sdist
pip install dist/slingshot-0.2.tar.gz --force-reinstall

# create new database user
mysql -u root --password=$MYSQL_PASS -e "create user 'slingshot'@'localhost' identified by 'slingshot';"
mysql -u root --password=$MYSQL_PASS -e "grant all privileges on slingshot.* to 'slingshot'@'localhost';"

# configure mysql to allow large packets (1G) and many connections
sudo sed -i -r "s/^(#\s*)?(max_allowed_packet\s*=\s*).*$/\21G/g" /etc/mysql/my.cnf
sudo sed -i -r "s/^(#\s*)?(max_connections\s*=\s*).*$/\2100/" /etc/mysql/my.cnf

# restart mysql daemon for the changes to take effect
sudo restart mysql
