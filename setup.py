from setuptools import setup

setup(name='hb_downloader',
      version='0.5.0',
      description='an unofficial api client for humblebundle',
      url='https://github.com/MayeulC/hb-downloader/releases',
      author='Brian Schkerke',
      license='MIT',
      packages=[
          'hb_downloader',
          'hb_downloader.humble_api',
          'hb_downloader.humble_api.model',
          'hb_downloader.humble_api.exceptions'
          ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
