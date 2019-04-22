
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

#for MAC with MacPorts:
sudo port install py36-numpy py36-scipy py36-matplotlib py36-ipython +notebook py36-pandas py36-sympy py36-nose

#for Ubuntu
sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose


