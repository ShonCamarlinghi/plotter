
#Ref: https://thepythonguru.com/python-virtualenv-guide/
#1. create project directory, set virtualenv 
mkdir plotter
cd plotter
virtualenv my_env
source my_env/bin/activate

#2.1 while in my_env dir, install/upgrade pip 
curl https://bootstrap.pypa.io/get-pip.py | python

#2.2 install packages for plotting
#for MAC:
python -m pip install numpy scipy matplotlib

#for Ubuntu
sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose


### troubleshooting
"   from matplotlib.backends import _macosx
RuntimeError: Python is not installed as a framework. The Mac OS X backend will not be able to function correctly if Python is not installed as a framework. See the Python documentation for more information on installing Python as a framework on Mac OS X. Please either reinstall Python as a framework, or try one of the other backends. If you are using (Ana)Conda please install python.app and replace the use of 'python' with 'pythonw'. See 'Working with Matplotlib on OSX' in the Matplotlib FAQ for more information.

Process finished with exit code 1 "
