from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, shell_cs

import re
import nginx
import os


class Gollum(Plugin):
	implements(apis.webapps.IWebapp)

	addtoblock = []

	def pre_install(self, name, vars):
		rubyctl = apis.langassist(self.app).get_interface('Ruby')
		rubyctl.install_gem('gollum', 'rdiscount')

	def post_install(self, name, path, vars, dbinfo={}):
		# Make sure the webapps config points to the _site directory and generate it.
		c = nginx.loadf(os.path.join('/etc/nginx/sites-available', name))
		for x in c.servers:
			if x.filter('Key', 'root'):
				x.filter('Key', 'root')[0].value = os.path.join(path, '_site')
		nginx.dumpf(c, os.path.join('/etc/nginx/sites-available', name))
		s = shell_cs('gollum build --source '+path+' --destination '+os.path.join(path, '_site'), stderr=True)
		if s[0] != 0:
			raise Exception('gollum failed to build: %s'%str(s[1]))
		shell('chmod 755 $(find %s -type d)' % path)
		shell('chmod 644 $(find %s -type f)' % path)
		shell('chown -R http:http %s' % path)

		# Return an explicatory message.
		return 'gollum has been setup, with a sample site at '+path+'. Modify these files as you like. To learn how to use gollum, visit https://github.com/gollum/gollum/wiki. After making changes, click the Configure button next to the site, then "Regenerate Site" to bring your changes live.'

	def pre_remove(self, site):
		pass

	def post_remove(self, site):
		pass

	def ssl_enable(self, path, cfile, kfile):
		pass

	def ssl_disable(self, path):
		pass

	def regenerate_site(self, site):
		s = shell_cs('gollum build --source '+site.path.rstrip('_site')+' --destination '+os.path.join(site.path), stderr=True)
		if s[0] != 0:
			raise Exception('gollum failed to build: %s'%str(s[1]))
		shell('chmod 755 $(find %s -type d)' % site.path.rstrip('_site'))
		shell('chmod 644 $(find %s -type f)' % site.path.rstrip('_site'))