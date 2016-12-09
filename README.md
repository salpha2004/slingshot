# slingshot

Slingshot is the fault-injection tool for RTEMS. It follows an approach taken by CMU's [Ballista] project and modified by [TUD DEED's Slingshot] project.

### Build and Run Instructions
(to manually build the repository refer to [README-manual.md])
0. Install [Vagrant].
1. Clone the repository (or just download the `vagrant` directory):
```sh
bash$ git clone https://github.com/salpha2004/slingshot/
```
2. Go to `vagrant` directory in `slingshot` and run:
```sh
bash$ vagrant up
```
3. After completion of the above command, ssh into the newly created box:
```sh
bash$ vagrant ssh
```

4. In the home directory of the box, there are two scripts: one for building rtems, one for running slingshot. Run them in order:
```sh
bash-vagrant-box$ bash ./build-rtems.sh
bash-vagrant-box$ bash ./run-slingshot.sh
```

Test suites would be generated in the `tmp` directory (default value), located under `slingshot` directory.

Each time you can re-run the test process by running `run-slingshot.sh` script.

- The instructions were tested on OS X 10.11.6 (El Capitan) using VirtualBox 5.0.24 and Vagrant 1.8.7 (NOTE: using VirtualBox 5.1.8 was troublesome)

[TUD DEED's Slingshot]: https://github.com/DEEDS-TUD/Slingshot
[Ballista]: http://www.cs.cmu.edu/afs/cs/project/edrc-ballista/www/
[Vagrant]: https://www.vagrantup.com/docs/getting-started/
[README-manual.md]: ./README-manual.md
