from setuptools import setup

setup(name='india-geosearch',
      version='0.1',
      description='Reverse geolocation API for india political boundaries',
      author='Anand Chitipothu',
      author_email='anandology@gmail.com',
      url='http://geosearch-anandology.rhccloud.com/',
      install_requires=['web.py', 'flup', 'psycopg2'],
     )
