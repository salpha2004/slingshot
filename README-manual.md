# slingshot

Slingshot is the fault-injection tool for RTEMS. It follows an approach taken by CMU's [Ballista] project and modified by [TUD DEED's Slingshot] project.

### Build and Run Instructions (manual, i.e. w/o Vagrant scripts)
0. Build RTEMS via [RSB] for your pc386 architecture.

**Dependencies**
1. Install the following list of packages.
* openssh-server
* build-essential
* git-core
* mysql-server
* python-mysqldb
* libmysqlclient15-dev
* python-dev
* libxml2-dev
* libxslt1-dev
* curl
* libbz2-dev
* libsqlite3-dev
* libgdbm-dev
* libssl-dev
* libexpat1-dev
* libncurses5-dev


**Python Environment**

2. To create multiple (virtual) Python environments, install [pyenv] and install Python 2.7.10 afterwards.
```sh
bash$ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
bash$ pyenv install 2.7.10
```

**slingshot**
3. Clone the repository and install slingshot.
```sh
bash$ git clone https://github.com/salpha2004/slingshot.git
bash$ cd slingshot
slingshot$ python ./setup.py sdist
slingshot$ pip install dist/slingshot-0.2.tar.gz --force-reinstall
```
4. Create a new database user.
```sh
slingshot$ mysql -e "create user 'slingshot'@'%' identified by 'slingshot';"
slingshot$ mysql -e "grant all privileges on *.* to 'slingshot'@'%';"
```
**For each time you want to generate and run test suites, do the following:**
5. Run the following script to initialize a new database and create the tables.
```sh
slingshot$ ./reinit-db.sh
```
6. Populate test stubs (A sample test case list named `sample.tcl` is in the `slingshot` directory).
```sh
slingshot$ init_db -t test-case-list.tcl
```
7. Run slingshot to generate test suites (NOTE: `slingshot -h` gives overview to different options).
```sh
slingshot$ slingshot
```

This takes quite a while depending on the size of the test case list.

By default, test suites are generated in the `tmp` directory, located under current directory.

[TUD DEED's Slingshot]: https://github.com/DEEDS-TUD/Slingshot
[Ballista]: http://www.cs.cmu.edu/afs/cs/project/edrc-ballista/www/
[RSB]: https://docs.rtems.org/rsb/ 
[pyenv]: https://github.com/yyuu/pyenv
