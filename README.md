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

| Device Boot | Start | End | Blocks | Id | System |
|---|---|---|---|---|---|
2015-05-05-raspbian-wheezy.img1 | 8192 | 122879 | 57344 | c | W95 FAT32 (LBA) |
2015-05-05-raspbian-wheezy.img2 | 122880 | 6399999 | 3138560 | 83 | Linux |

## Mount the image
* `mkdir ~/rpi_mnt
* `sudo mount 2015-05-05-raspbian-wheezy.img -o loop,offset=$((122880*512)),rw ~/rpi_mnt`

## (OPTIONAL) mount the raspbian /boot
* `sudo mount 2015-05-05-raspbian-wheezy.img -o loop,offset=$((8192*512)),rw ~/rpi_mnt/boot`

or

* `cd ~/rpi_mnt`
* `sudo mount --bind /dev dev/`
* `sudo mount --bind /sys sys/`
* `sudo mount --bind /proc proc/`
* `sudo mount --bind /dev/pts dev/pts`

## Network working

To get everything work (e.g., network) you need to comment out everything in ~/rpi_mnt/etc/ld.so.preload before chrooting in. Take care of that now!

## chroot in to the image
* `sudo cp /usr/bin/qemu-arm-static ~/rpi_mnt/usr/bin`
* `cd ~/rpi_mnt`
* `sudo chroot . bin/bash` 

```
$ sudo chroot . bin/bash
root@ubuntu:/# uname -a
Linux ubuntu 3.13.0-24-generic #46-Ubuntu SMP Thu Apr 10 19:11:08 UTC 2014 armv7l GNU/Linux
```

## Starting http server
* `python -m SimpleHTTPServer 8081`

Access localhost:8081 in browser and you will see the / in raspberry pi image.

## (OPTIONAL) Adding 1GB Space
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

| Device Boot | Start | End | Blocks | Id | System |
|---|---|---|---|---|---|
2015-05-05-raspbian-wheezy.img1 | 8192 | 122879 | 57344 | c | W95 FAT32 (LBA) |
2015-05-05-raspbian-wheezy.img2 | 122880 | 6399999 | 3138560 | 83 | Linux |
 

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

``` 
Model: Loopback device (loop)

Disk /dev/loop0: 4351MB

Sector size (logical/physical): 512B/512B

Partition Table: msdos
``` 

| Number | Start |  End | Size | Type | File system | Flags |
|---|---|---|---|---|---|---|
| 1 | 4194kB | 62.9MB | 58.7MB | primary | fat16 | lba |
| 2 | 62.9MB | 3277MB | 3214MB | primary | ext4 | |

* `(parted) rm 2`
* `(parted) mkpart primary 62.9 4351`
* `(parted) print`

``` 
Model: Loopback device (loop)
Disk /dev/loop0: 4351MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos

Number  Start   End     Size    Type     File system  Flags
 1      4194kB  62.9MB  58.7MB  primary  fat16        lba
 2      62.9MB  4351MB  4288MB  primary  ext4
``` 

* `(parted) quit`

Next, check and resize the new partition:
* `sudo e2fsck -f /dev/loop1`

``` 
e2fsck 1.42.9 (4-Feb-2014)
Pass 1: Checking inodes, blocks, and sizes
Pass 2: Checking directory structure
Pass 3: Checking directory connectivity
Pass 4: Checking reference counts
Pass 5: Checking group summary information
/dev/loop1: 86233/196224 files (0.1% non-contiguous), 630146/784640 blocks
``` 

* `sudo resize2fs /dev/loop1`

``` 
resize2fs 1.42.9 (4-Feb-2014)
Resizing the filesystem on /dev/loop1 to 1046784 (4k) blocks.
The filesystem on /dev/loop1 is now 1046784 blocks long.
``` 

### Checking resizing
And you can check that it worked, it's 1 GB larger!
* `sudo parted /dev/loop0`
* `(parted) print`

``` 
Model: Loopback device (loop)
Disk /dev/loop0: 4351MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos

Number  Start   End     Size    Type     File system  Flags
 1      4194kB  62.9MB  58.7MB  primary  fat16        lba
 2      62.9MB  4351MB  4288MB  primary  ext4
``` 

### Clean up loopback devices
* `sudo losetup -d /dev/loop0 /dev/loop1`

## Creating SD Card

Before you need to clean it (if you chroot it and mounted the image):
* uncomment /etc/ld.so.preload
* exit the chroot (e.g., type "exit")
* unmount all that was mounted

* `sudo umount ~/rpi_mnt/dev` 
* `sudo umount ~/rpi_mnt/sys`
* `sudo umount ~/rpi_mnt/proc`
* `sudo umount ~/rpi_mnt/dev/pts`
* `sudo umount ~/rpi_mnt/boot`
* `sudo umount ~/rpi_mnt`

* your image is still in ~/rpi_image and ready to be flashed!

## Python env
* `sudo apt-get update`
* `sudo apt-get install python-pip python-dev build-essential`
* `sudo pip install --upgrade pip`
* `sudo pip install --upgrade virtualenv`
* `sudo apt-get install vim`

## Flask Sample
* `sudo su pi`
* `cd`
* `mkdir flask_sample`
* `cd flask_sample`
* `vim requirements.txt`

Add flask dependency in requirements.txt (No specific version):

```
flask
```

### Create virtualenv
* `virtualenv venv_flask_sample`
* `source venv_flask_sample/bin/activate`
* `pip install -r requirements.txt`

### Create app.py
* `vim app.py`

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
```

* `python app.py`

```
```

## Flask Post Method

Before main in app.py add this piece of code:

```
from datetime import datetime
from flask import request
from flask import jsonify

@app.route('/api/alert/email', methods=['POST'])
def alert_by_email():
    content = request.get_json()
    content['received_at'] = datetime.now()
    return jsonify({'received': content}), 200
```

* `python app.py`

Install curl in host and execute the post method:
* `sudo apt-get install curl`
* `curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/api/alert/email`

## Adding Template

Create a directory called templates in src folder:

* mkdir src/templates

```
[4256:4244 - 0:442] 10:19:55 [dinesh@ubuntu:o +1] ~/work/solo/raspberry_flask (master)  
$ ls src/
app.py  templates

```

With a text editor create and edit a file called src/templates/index.html

```
<html>
<body>
<h1>Hello from a template!</h1>
</body>
</html>
```

```
from flask import render_template

@app.route('/hellotemplate')
def hello_template():
    return render_template('index.html')
```

## Adding Dynamic Template (jinja2)

* Create a new route

``` 
@app.route('/hello/<name>')
def hello(name):
    return render_template('page.html', name=name)
```

* Create a new html file called src/templates/page.html

```
<h1>Hello {{ name }}!</h1>
```

## Adding static file (CSS ou Js)

Create a directory called static in src folder:

* mkdir src/static

```
[4256:4244 - 0:446] 10:30:26 [dinesh@ubuntu:o +1] ~/work/solo/raspberry_flask (master)  
$ ls src
app.py  static  templates
```

* Create a new css file called style.css

``` 
body {
    background: red;
    color: yellow;
}
```

* Now edit src/templates/index.html

```
<html>
<head>
<link rel="stylesheet" href='/static/style.css' />
</head>
<body>
<h1>Hello from a template!</h1>
</body>
</html>
```

### SD Cards - References

* [Installation](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)
* [Linux Installation](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md)

###  Raspberry pi References
* [Wiki Debian](https://wiki.debian.org/RaspberryPi/qemu-user-static)
* [Raspbian official](https://www.raspbian.org/FrontPage)

### Flask References
* [Flask + Raspberry pi](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)