# Pinehead Records webapp v0

This version features:

- Relational model in MySQL
- limited optimizations
- limited caching
- no indexes
- inefficient queries
- images stored on local filesystem
  - symlink `/webapp/static/albumart` to wherever `albumart.zip` is extracted
- accounts in DB
  
## Setup for Amazon Linux 2

## Configure AWS Region

Write the following to `~/.aws/config` if you have not already run `aws configure`:

```text
[default]
region=us-east-1
```
## Install Packages

```sh
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-pip python3 python3-devel python3-setuptools git mariadb mariadb-devel mariadb-server
sudo systemctl start mariadb
sudo mysql_secure_installation # set a root password and other options
sudo systemctl stop mariadb
sudo systemctl enable mariadb
sudo systemctl start mariadb

mysql -uroot -p
CREATE USER 'pinehead'@'localhost' IDENTIFIED BY 'pinehead';
GRANT ALL PRIVILEGES ON * . * TO 'pinehead'@'localhost';
FLUSH PRIVILEGES;
CREATE DATABASE pinehead;
exit;
```

### Restore MySQL database

```sh
aws s3 cp s3://dynamodblabs/pineheadrecords.sql .
mysql -uroot -p pinehead < pineheadrecords.sql
```

```sh
git clone <url to repo>
cd <path to project>
pipenv install
pipenv shell
pip3 install --user pipenv
```

## Run the Flask app

Ensure you are running in a virtual environment. If not, run `pipenv shell`.

Start the web server:

`./run.sh`

or

```sh
FLASK_APP=webapp FLASK_ENV=development flask run --host=0.0.0.0
```
