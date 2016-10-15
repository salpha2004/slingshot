# slingshot

Slingshot is the fault-injection tool for RTEMS. It follows an approach taken by CMU's [Ballista] project and modified by [TUD DEED's Slingshot] project.

### Build and Run Instructions
(to manually build the repository refer to [README-manual.md])
0. Install [Vagrant].
1. Go to `vagrant` directory and run:
```sh
bash$ vagrant up
```
2. After completion of the above command, ssh into the newly created box:
```sh
bash$ vagrant ssh
```
3. In the home directory of the box, there are two scripts: one for building rtems, one for running slingshot. Run them in order:
```sh
bash-vagrant-box$ bash ./build-rtems.sh
bash-vagrant-box$ bash ./run-slingshot.sh
```

Test suites would be generated in the `tmp` directory (default value), located under `slingshot` directory.


[TUD DEED's Slingshot]: https://github.com/DEEDS-TUD/Slingshot
[Ballista]: http://www.cs.cmu.edu/afs/cs/project/edrc-ballista/www/
[Vagrant]: http://vagrantup.com/
[README-manual.md]: ./README-manual.md
