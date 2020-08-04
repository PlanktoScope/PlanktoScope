#########################################################
Installation of MorphoCut development version:
#########################################################

$ pip install -U git+https://github.com/morphocut/morphocut.git
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Collecting git+https://github.com/morphocut/morphocut.git
  Cloning https://github.com/morphocut/morphocut.git to /tmp/pip-req-build-NnGYk4
  Installing build dependencies ... error
  Complete output from command /usr/bin/python -m pip install --ignore-installed --no-user --prefix /tmp/pip-build-env-e4DHrk --no-warn-script-location --no-binary :none: --only-binary :none: -i https://pypi.org/simple --extra-index-url https://www.piwheels.org/simple -- setuptools wheel:
  Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple, https://www.piwheels.org/simple
  Collecting setuptools
    Downloading https://www.piwheels.org/simple/setuptools/setuptools-45.0.0-py2.py3-none-any.whl (583kB)
  setuptools requires Python '>=3.5' but the running Python is 2.7.16
  
  ----------------------------------------
Command "/usr/bin/python -m pip install --ignore-installed --no-user --prefix /tmp/pip-build-env-e4DHrk --no-warn-script-location --no-binary :none: --only-binary :none: -i https://pypi.org/simple --extra-index-url https://www.piwheels.org/simple -- setuptools wheel" failed with error code 1 in None

#########################################################
Installation of MorphoCut packaged on PyPI via pip
#########################################################

$ pip install morphocut
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Collecting morphocut
  Could not find a version that satisfies the requirement morphocut (from versions: )
No matching distribution found for morphocut

#########################################################
Installation of MorphoCut packaged on PyPI via pip3
#########################################################

$ pip3 install morphocut
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Collecting morphocut
  Downloading https://files.pythonhosted.org/packages/7e/c7/1addaf867234dd30db6d1f4bf8d3b685d93b743023a863814451abd5cef8/morphocut-0.1.1-py3-none-any.whl
Collecting scikit-image>=0.16.0 (from morphocut)
  Downloading https://www.piwheels.org/simple/scikit-image/scikit_image-0.16.2-cp37-cp37m-linux_armv7l.whl (39.7MB)
    100% |████████████████████████████████| 39.7MB 10kB/s 
Collecting tqdm (from morphocut)
  Downloading https://files.pythonhosted.org/packages/72/c9/7fc20feac72e79032a7c8138fd0d395dc6d8812b5b9edf53c3afd0b31017/tqdm-4.41.1-py2.py3-none-any.whl (56kB)
    100% |████████████████████████████████| 61kB 1.6MB/s 
Collecting scipy (from morphocut)
  Downloading https://files.pythonhosted.org/packages/04/ab/e2eb3e3f90b9363040a3d885ccc5c79fe20c5b8a3caa8fe3bf47ff653260/scipy-1.4.1.tar.gz (24.6MB)
    100% |████████████████████████████████| 24.6MB 17kB/s 
  Installing build dependencies ... done
Requirement already satisfied: numpy in /usr/lib/python3/dist-packages (from morphocut) (1.16.2)
Collecting pandas (from morphocut)
  Downloading https://www.piwheels.org/simple/pandas/pandas-0.25.3-cp37-cp37m-linux_armv7l.whl (33.1MB)
    100% |████████████████████████████████| 33.1MB 12kB/s 
Collecting PyWavelets>=0.4.0 (from scikit-image>=0.16.0->morphocut)
  Downloading https://www.piwheels.org/simple/pywavelets/PyWavelets-1.1.1-cp37-cp37m-linux_armv7l.whl (6.1MB)
    100% |████████████████████████████████| 6.1MB 67kB/s 
Collecting networkx>=2.0 (from scikit-image>=0.16.0->morphocut)
  Downloading https://files.pythonhosted.org/packages/41/8f/dd6a8e85946def36e4f2c69c84219af0fa5e832b018c970e92f2ad337e45/networkx-2.4-py3-none-any.whl (1.6MB)
    100% |████████████████████████████████| 1.6MB 255kB/s 
Requirement already satisfied: pillow>=4.3.0 in /usr/lib/python3/dist-packages (from scikit-image>=0.16.0->morphocut) (5.4.1)
Collecting imageio>=2.3.0 (from scikit-image>=0.16.0->morphocut)
  Downloading https://files.pythonhosted.org/packages/1a/de/f7f985018f462ceeffada7f6e609919fbcc934acd9301929cba14bc2c24a/imageio-2.6.1-py3-none-any.whl (3.3MB)
    100% |████████████████████████████████| 3.3MB 123kB/s 
Collecting python-dateutil>=2.6.1 (from pandas->morphocut)
  Downloading https://files.pythonhosted.org/packages/d4/70/d60450c3dd48ef87586924207ae8907090de0b306af2bce5d134d78615cb/python_dateutil-2.8.1-py2.py3-none-any.whl (227kB)
    100% |████████████████████████████████| 235kB 822kB/s 
Collecting pytz>=2017.2 (from pandas->morphocut)
  Downloading https://files.pythonhosted.org/packages/e7/f9/f0b53f88060247251bf481fa6ea62cd0d25bf1b11a87888e53ce5b7c8ad2/pytz-2019.3-py2.py3-none-any.whl (509kB)
    100% |████████████████████████████████| 512kB 660kB/s 
Collecting decorator>=4.3.0 (from networkx>=2.0->scikit-image>=0.16.0->morphocut)
  Downloading https://files.pythonhosted.org/packages/8f/b7/f329cfdc75f3d28d12c65980e4469e2fa373f1953f5df6e370e84ea2e875/decorator-4.4.1-py2.py3-none-any.whl
Requirement already satisfied: six>=1.5 in /usr/lib/python3/dist-packages (from python-dateutil>=2.6.1->pandas->morphocut) (1.12.0)
Building wheels for collected packages: scipy
  Running setup.py bdist_wheel for scipy ... error
  Complete output from command /usr/bin/python3 -u -c "import setuptools, tokenize;__file__='/tmp/pip-install-vrivsnzz/scipy/setup.py';f=getattr(tokenize, 'open', open)(__file__);code=f.read().replace('\r\n', '\n');f.close();exec(compile(code, __file__, 'exec'))" bdist_wheel -d /tmp/pip-wheel-2w9xwni0 --python-tag cp37:
  Traceback (most recent call last):
    File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/core/__init__.py", line 16, in <module>
      from . import multiarray
  ImportError: libf77blas.so.3: cannot open shared object file: No such file or directory
  
  During handling of the above exception, another exception occurred:
  
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "/tmp/pip-install-vrivsnzz/scipy/setup.py", line 540, in <module>
      setup_package()
    File "/tmp/pip-install-vrivsnzz/scipy/setup.py", line 516, in setup_package
      from numpy.distutils.core import setup
    File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/__init__.py", line 142, in <module>
      from . import add_newdocs
    File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/add_newdocs.py", line 13, in <module>
      from numpy.lib import add_newdoc
    File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/lib/__init__.py", line 8, in <module>
      from .type_check import *
    File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/lib/type_check.py", line 11, in <module>
      import numpy.core.numeric as _nx
    File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/core/__init__.py", line 26, in <module>
      raise ImportError(msg)
  ImportError:
  Importing the multiarray numpy extension module failed.  Most
  likely you are trying to import a failed build of numpy.
  If you're working with a numpy git repo, try `git clean -xdf` (removes all
  files not under version control).  Otherwise reinstall numpy.
  
  Original error was: libf77blas.so.3: cannot open shared object file: No such file or directory
  
  
  ----------------------------------------
  Failed building wheel for scipy
  Running setup.py clean for scipy
  Complete output from command /usr/bin/python3 -u -c "import setuptools, tokenize;__file__='/tmp/pip-install-vrivsnzz/scipy/setup.py';f=getattr(tokenize, 'open', open)(__file__);code=f.read().replace('\r\n', '\n');f.close();exec(compile(code, __file__, 'exec'))" clean --all:
  
  `setup.py clean` is not supported, use one of the following instead:
  
    - `git clean -xdf` (cleans all files)
    - `git clean -Xdf` (cleans all versioned files, doesn't touch
                        files that aren't checked into the git repo)
  
  Add `--force` to your command to use it anyway if you must (unsupported).
  
  
  ----------------------------------------
  Failed cleaning build dir for scipy
Failed to build scipy
Installing collected packages: PyWavelets, decorator, networkx, imageio, scikit-image, tqdm, scipy, python-dateutil, pytz, pandas, morphocut
  Running setup.py install for scipy ... error
    Complete output from command /usr/bin/python3 -u -c "import setuptools, tokenize;__file__='/tmp/pip-install-vrivsnzz/scipy/setup.py';f=getattr(tokenize, 'open', open)(__file__);code=f.read().replace('\r\n', '\n');f.close();exec(compile(code, __file__, 'exec'))" install --record /tmp/pip-record-s4uxcq_l/install-record.txt --single-version-externally-managed --compile --user --prefix=:
    
    Note: if you need reliable uninstall behavior, then install
    with pip instead of using `setup.py install`:
    
      - `pip install .`       (from a git repo or downloaded source
                               release)
      - `pip install scipy`   (last SciPy release on PyPI)
    
    
    Traceback (most recent call last):
      File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/core/__init__.py", line 16, in <module>
        from . import multiarray
    ImportError: libf77blas.so.3: cannot open shared object file: No such file or directory
    
    During handling of the above exception, another exception occurred:
    
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/tmp/pip-install-vrivsnzz/scipy/setup.py", line 540, in <module>
        setup_package()
      File "/tmp/pip-install-vrivsnzz/scipy/setup.py", line 516, in setup_package
        from numpy.distutils.core import setup
      File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/__init__.py", line 142, in <module>
        from . import add_newdocs
      File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/add_newdocs.py", line 13, in <module>
        from numpy.lib import add_newdoc
      File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/lib/__init__.py", line 8, in <module>
        from .type_check import *
      File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/lib/type_check.py", line 11, in <module>
        import numpy.core.numeric as _nx
      File "/tmp/pip-build-env-3v411zsn/lib/python3.7/site-packages/numpy/core/__init__.py", line 26, in <module>
        raise ImportError(msg)
    ImportError:
    Importing the multiarray numpy extension module failed.  Most
    likely you are trying to import a failed build of numpy.
    If you're working with a numpy git repo, try `git clean -xdf` (removes all
    files not under version control).  Otherwise reinstall numpy.
    
    Original error was: libf77blas.so.3: cannot open shared object file: No such file or directory
    
    
    ----------------------------------------
Command "/usr/bin/python3 -u -c "import setuptools, tokenize;__file__='/tmp/pip-install-vrivsnzz/scipy/setup.py';f=getattr(tokenize, 'open', open)(__file__);code=f.read().replace('\r\n', '\n');f.close();exec(compile(code, __file__, 'exec'))" install --record /tmp/pip-record-s4uxcq_l/install-record.txt --single-version-externally-managed --compile --user --prefix=" failed with error code 1 in /tmp/pip-install-vrivsnzz/scipy/
#########################################################
Installation of Scipy using sudo apt-get
#########################################################

$ sudo apt-get install python3-scipy
Lecture des listes de paquets... Fait
Construction de l'arbre des dépendances       
Lecture des informations d'état... Fait
Les paquets supplémentaires suivants seront installés : 
  python3-decorator
Paquets suggérés :
  python-scipy-doc
Les NOUVEAUX paquets suivants seront installés :
  python3-decorator python3-scipy
0 mis à jour, 2 nouvellement installés, 0 à enlever et 41 non mis à jour.
Il est nécessaire de prendre 8 925 ko dans les archives.
Après cette opération, 38,0 Mo d'espace disque supplémentaires seront utilisés.
Souhaitez-vous continuer ? [O/n] o
Réception de :1 http://ftp.igh.cnrs.fr/pub/os/linux/raspbian/raspbian buster/main armhf python3-decorator all 4.3.0-1.1 [14,5 kB]
Réception de :2 http://ftp.igh.cnrs.fr/pub/os/linux/raspbian/raspbian buster/main armhf python3-scipy armhf 1.1.0-7 [8 910 kB]
8 925 ko réceptionnés en 3s (2 561 ko/s)       
Sélection du paquet python3-decorator précédemment désélectionné.
(Lecture de la base de données... 99960 fichiers et répertoires déjà installés.)
Préparation du dépaquetage de .../python3-decorator_4.3.0-1.1_all.deb ...
Dépaquetage de python3-decorator (4.3.0-1.1) ...
Sélection du paquet python3-scipy précédemment désélectionné.
Préparation du dépaquetage de .../python3-scipy_1.1.0-7_armhf.deb ...
Dépaquetage de python3-scipy (1.1.0-7) ...
Paramétrage de python3-decorator (4.3.0-1.1) ...
Paramétrage de python3-scipy (1.1.0-7) ...

#########################################################
Installation of MorphoCut packaged on PyPI via pip3 using sudo
#########################################################

$ sudo pip3 install morphocut
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Collecting morphocut
  Using cached https://files.pythonhosted.org/packages/7e/c7/1addaf867234dd30db6d1f4bf8d3b685d93b743023a863814451abd5cef8/morphocut-0.1.1-py3-none-any.whl
Requirement already satisfied: scikit-image>=0.16.0 in /usr/local/lib/python3.7/dist-packages (from morphocut) (0.16.2)
Requirement already satisfied: numpy in /usr/lib/python3/dist-packages (from morphocut) (1.16.2)
Requirement already satisfied: tqdm in /usr/local/lib/python3.7/dist-packages (from morphocut) (4.41.1)
Requirement already satisfied: pandas in /usr/local/lib/python3.7/dist-packages (from morphocut) (0.25.3)
Requirement already satisfied: scipy in /usr/lib/python3/dist-packages (from morphocut) (1.1.0)
Requirement already satisfied: imageio>=2.3.0 in /usr/local/lib/python3.7/dist-packages (from scikit-image>=0.16.0->morphocut) (2.6.1)
Requirement already satisfied: PyWavelets>=0.4.0 in /usr/local/lib/python3.7/dist-packages (from scikit-image>=0.16.0->morphocut) (1.1.1)
Requirement already satisfied: networkx>=2.0 in /usr/local/lib/python3.7/dist-packages (from scikit-image>=0.16.0->morphocut) (2.4)
Requirement already satisfied: pillow>=4.3.0 in /usr/lib/python3/dist-packages (from scikit-image>=0.16.0->morphocut) (5.4.1)
Requirement already satisfied: python-dateutil>=2.6.1 in /usr/local/lib/python3.7/dist-packages (from pandas->morphocut) (2.8.1)
Requirement already satisfied: pytz>=2017.2 in /usr/local/lib/python3.7/dist-packages (from pandas->morphocut) (2019.3)
Requirement already satisfied: decorator>=4.3.0 in /usr/local/lib/python3.7/dist-packages (from networkx>=2.0->scikit-image>=0.16.0->morphocut) (4.4.1)
Requirement already satisfied: six>=1.5 in /usr/lib/python3/dist-packages (from python-dateutil>=2.6.1->pandas->morphocut) (1.12.0)
Installing collected packages: morphocut
Successfully installed morphocut-0.1.1
