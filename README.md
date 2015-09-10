# RasBerry Pi and Flask Application

## Setup Host
* `sudo apt-get install qemu qemu-user-static binfmt-support`

## Checking ARM support
* `update-binfmts --display`

Expected:
``
...
qemu-arm (enabled):
     package = qemu-user-static
        type = magic
      offset = 0
       magic = \x7fELF\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x28\x00
        mask = \xff\xff\xff\xff\xff\xff\xff\x00\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff
 interpreter = /usr/bin/qemu-arm-static
    detector = 
...
``

## Download Raspbian Image
* [Raspbian Image](https://www.raspberrypi.org/downloads/)
or
* `wget https://downloads.raspberrypi.org/raspbian_latest`

## Creating SD Card
* [Installation](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)
* [Linux Installation](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md)

## References
* [Wiki Debian](https://wiki.debian.org/RaspberryPi/qemu-user-static)
* [Raspbian official](https://www.raspbian.org/FrontPage)