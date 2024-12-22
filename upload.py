#!/usr/bin/env python3

"""
www-data ALL=(ALL) NOPASSWD: /usr/lib/cgi-bin/upload.py
www-data ALL=(ALL) NOPASSWD: /usr/bin/mount
www-data ALL=(ALL) NOPASSWD: /usr/bin/umount
www-data ALL=(ALL) NOPASSWD: /usr/bin/eject
www-data ALL=(ALL) NOPASSWD: /usr/bin/cp
www-data ALL=(ALL) NOPASSWD: /usr/bin/ls
"""

import cgi
import os
import datetime
import subprocess

UPLOAD_DIR = '/media/usb'

def is_mounted(mount_point):
    with open('/proc/mounts', 'r') as f:
        mounts = f.readlines()
    for mount in mounts:
        if mount_point in mount:
            print (f"MOUNT {mount}<br/> ")
            return True
    return False

def list_usb_block_devices():
    # Run lsblk command and capture the output
    result = subprocess.run(['lsblk', '-o', 'NAME,TRAN'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    # Filter the output to show only USB devices
    usb_devices = [line.split()[0] for line in output.splitlines() if 'usb' in line]

    return usb_devices

def format_number(num):
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}G"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}k"
    else:
        return str(num)

mount_point = '/media/usb'
def main():
    form = cgi.FieldStorage()
    print("Content-Type: text/html\n")

    subprocess.run(["sudo", "/usr/bin/umount", "/media/usb"], check=False, stderr=subprocess.PIPE)
    with open("/var/www/html/upload.html") as fd:
        for x in fd.readlines():
            print (x)
    devs = list_usb_block_devices()
    if (len(devs)>1):
        print (f"{len(devs)} USB devices found")
        print ("</body></html>")
        return 0
    if (len(devs)==0):
        print (f"No USB devices found")
        print ("</body></html>")
        return 0
    dev = f"/dev/{devs[0]}1"
    bdev = f"/dev/{devs[0]}"
    if 'eject' in form:
        subprocess.run(['sudo','/usr/bin/umount',dev])
        subprocess.run(['sudo','/usr/bin/eject',bdev])
        print ("<h2>Ejected</h2>")
        print ("</body></html>")
        return (0)

    if not is_mounted(mount_point):
        try:
            subprocess.run(["sudo",'/usr/bin/mount', "-o", "rw,uid=www-data,gid=www-data,fmask=0022,dmask=0022",dev,'/media/usb'],check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"{mount_point} Mount failed: {e.stderr.decode()}")
            print ("</body></html>")
            return
        except BaseException as e:
            print(f"{mount_point} is not mounted {e}")
            print ("</body></html>")
            return
    """
    print ("MOUNTED")
    print ("<pre>")
    print ("FILES")
    print (subprocess.run(['sudo','/usr/bin/ls','-ld','/media/usb'],capture_output=True).stdout.decode('utf-8'))
    print (subprocess.run(['sudo','/usr/bin/ls','-l','/media/usb'],capture_output=True,check=True).stdout.decode('utf-8'))
    print ("</pre>")
    """
    print ("<table style=\"font-size:small;font-family:monospace\">\n")
    files=[]
    for x in os.listdir("/media/usb"):
        st = os.stat(path="/media/usb/"+x)
        files.append({
            'name': x,
            'st': st
            })
    for f in sorted(files, reverse=True, key=lambda f: f['st'].st_mtime):
        creation_time = datetime.datetime.fromtimestamp(f['st'].st_mtime)
        creation_time_str = creation_time.strftime('%Y-%m-%d %H:%M:%S')
        print (f"<tr><td><input type=\"checkbox\" /></td><td>{f['name']}</td><td style=\"text-align:right;padding-right:20px\">{format_number(f['st'].st_size)}</td><td>{creation_time_str}</td></td>\n")
    print ("</table>\n")


    if 'file' in form:
        files = form['file']
        if not isinstance(files,list):
            files=[files]
        for file_item in files:
            if file_item.filename:
                file_path = os.path.join(UPLOAD_DIR, os.path.basename(file_item.filename))
                with open("/tmp/tempfile", 'wb') as f:
                    f.write(file_item.file.read())
                subprocess.run(['sudo','/usr/bin/cp','/tmp/tempfile',file_path])
                subprocess.run(['sudo','/usr/bin/sync',dev])
                print(f"<p>File '{file_item.filename}' uploaded successfully!</p>")
        else:
            print("<p>No file was uploaded.</p>")

    print ("</body></html>")
if __name__ == "__main__":
    main()

