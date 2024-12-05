# Upload

Stupid web utility to upload files directly to USB media

# Directions

install `upload.cgi` to `/usr/lib/cgi-bin/` and `upload.html` to `/usr/www/html`. Make sure you set up CGI directories

You will need to set up `/etc/sudoers` something like:

```
www-data ALL=(ALL) NOPASSWD: /usr/lib/cgi-bin/upload.py
www-data ALL=(ALL) NOPASSWD: /usr/bin/mount
www-data ALL=(ALL) NOPASSWD: /usr/bin/umount
www-data ALL=(ALL) NOPASSWD: /usr/bin/eject
www-data ALL=(ALL) NOPASSWD: /usr/bin/cp
www-data ALL=(ALL) NOPASSWD: /usr/bin/ls
```
