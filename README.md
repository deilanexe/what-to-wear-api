Pre-requirements for AWS EC2
==

sudo yum install gcc

sudo yum install libtiff-devel libjpeg-devel libzip-devel freetype-devel lcms2-devel libwebp-devel tcl-devel tk-devel

Then install Python libraries in requirements.txt

Create a file config.py in wtwapi/wtwapi/config/. Use config.duplicate.py as reference.

If required, start nginx and gunicorn as indicated in this page: https://www.matthealy.com.au/blog/post/deploying-flask-to-amazon-web-services-ec2/

disown processes and let API run!
