To run this, you'll need to install some modules and dictionary files.

This assumes you've made a virtualenv and are working in it.

The easy way:
	Run install.sh 

The hard way:
	Run `pip install -r requirements.txt`
	You'll need libxml2 and libxlst development packages to use on Linux
		apt-get install libxml2-dev libxlst1-dev

You can start Celery by running the celery.sh file.
