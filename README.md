# RasBerry Pi and Flask Application

## Setup Host
* `sudo apt-get install qemu qemu-user-static binfmt-support`

## Checking ARM support
* `update-binfmts --display`

Expected:
``` 
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
```

## Download Raspbian Image
* [Raspbian Image](https://www.raspberrypi.org/downloads/)

or

* `mkdir -p ~/qemu/images`
* `cd ~/qemu/images`
* `wget https://downloads.raspberrypi.org/raspbian_latest -O ~/qemu/images/raspbian.zip`
* `unzip raspbian.zip`

## Checking Disk Size
* `fdisk -lu 2015-05-05-raspbian-wheezy.img`

Expected:
``` 
Disk 2015-05-05-raspbian-wheezy.img: 3276 MB, 3276800000 bytes
255 heads, 63 sectors/track, 398 cylinders, total 6400000 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0xa6202af7
``` 
``
| Device Boot | Start | End | Blocks | Id | System |
|---|---|---|---|---|---|
2015-05-05-raspbian-wheezy.img1 | 8192 | 122879 | 57344 | c | W95 FAT32 (LBA) |
2015-05-05-raspbian-wheezy.img2 | 122880 | 6399999 | 3138560 | 83 | Linux |
`` 

## Adding 1GB Space
* `dd if=/dev/zero bs=1M count=1024 >> 2015-05-05-raspbian-wheezy.img`

Expected:
``` 
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB) copied, 3.00026 s, 358 MB/s
``` 

* `fdisk -lu 2015-05-05-raspbian-wheezy.img`
``` 
Disk 2015-05-05-raspbian-wheezy.img: 4350 MB, 4350541824 bytes

255 heads, 63 sectors/track, 528 cylinders, total 8497152 sectors

Units = sectors of 1 * 512 = 512 bytes

Sector size (logical/physical): 512 bytes / 512 bytes

I/O size (minimum/optimal): 512 bytes / 512 bytes

Disk identifier: 0xa6202af7
``` 
``
| Device Boot | Start | End | Blocks | Id | System |
|---|---|---|---|---|---|
2015-05-05-raspbian-wheezy.img1 | 8192 | 122879 | 57344 | c | W95 FAT32 (LBA) |
2015-05-05-raspbian-wheezy.img2 | 122880 | 6399999 | 3138560 | 83 | Linux |
`` 

### Loopback device
Make a loopback device for the whole image, and one for the raspbian root (which we found starts 122880 sectors in and each sector is 512 bytes)

* `sudo losetup -f --show 2015-05-05-raspbian-wheezy.img`
* `sudo losetup -f --show -o $((122880*512)) 2015-05-05-raspbian-wheezy.img`

It should create /dev/loop0 and /dev/loop1. To show all loopback device run the command:
* `sudo losetup -a`

Expected:
``
/dev/loop0: [0801]:1575893 (/home/dinesh/qemu/images/2015-05-05-raspbian-wheezy.img)
/dev/loop1: [0801]:1575893 (/home/dinesh/qemu/images/2015-05-05-raspbian-wheezy.img), offset 62914560
``

To delete loopback device:
* `sudo losetup -d /dev/loopX`

Now /dev/loop0 is the whole partition, /dev/loop1 is what we want to expand. In parted, remove the second partition, resize it to be the full size of /dev/loop0.

* `sudo parted /dev/loop0`

### parted Commands
* `(parted) print`

``
Model: Loopback device (loop)

Disk /dev/loop0: 4351MB

Sector size (logical/physical): 512B/512B

Partition Table: msdos

| Number | Start |  End | Size | Type | File system | Flags |
|---|---|---|---|---|---|---|
| 1 | 4194kB | 62.9MB | 58.7MB | primary | fat16 | lba |
| 2 | 62.9MB | 3277MB | 3214MB | primary | ext4 | |
``

* `(parted) rm 2`
* `(parted) mkpart primary 62.9 4351`
* `(parted) print`
``
Model: Loopback device (loop)
Disk /dev/loop0: 4351MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos

Number  Start   End     Size    Type     File system  Flags
 1      4194kB  62.9MB  58.7MB  primary  fat16        lba
 2      62.9MB  4351MB  4288MB  primary  ext4
``

* `(parted) quit`

Next, check and resize the new partition:
* `sudo e2fsck -f /dev/loop1`
``
e2fsck 1.42.9 (4-Feb-2014)
Pass 1: Checking inodes, blocks, and sizes
Pass 2: Checking directory structure
Pass 3: Checking directory connectivity
Pass 4: Checking reference counts
Pass 5: Checking group summary information
/dev/loop1: 86233/196224 files (0.1% non-contiguous), 630146/784640 blocks
``

* `sudo resize2fs /dev/loop1`
``
resize2fs 1.42.9 (4-Feb-2014)
Resizing the filesystem on /dev/loop1 to 1046784 (4k) blocks.
The filesystem on /dev/loop1 is now 1046784 blocks long.
``

### Checking resizing
And you can check that it worked, it's 1 GB larger!
* `sudo parted /dev/loop0`
* `(parted) print`
``
Model: Loopback device (loop)
Disk /dev/loop0: 4351MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos

Number  Start   End     Size    Type     File system  Flags
 1      4194kB  62.9MB  58.7MB  primary  fat16        lba
 2      62.9MB  4351MB  4288MB  primary  ext4

``

### Clean up loopback devices
* `sudo losetup -d /dev/loop0 /dev/loop1`

## Creating SD Card
* [Installation](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)
* [Linux Installation](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md)

## References
* [Wiki Debian](https://wiki.debian.org/RaspberryPi/qemu-user-static)
* [Raspbian official](https://www.raspbian.org/FrontPage)