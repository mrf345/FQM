#!/bin/bash
# Read me : this script will install FQM requirements and your user into the
# printing group. this script only meant to be run once before you run FQM for
# the first time

# checking if pip exist
pip_exi=`command -v pip`
pip2_exi=`command -v pip2`
# checking if python exist
python2=`command -v python2`
python=`command -v python`
# checking if qt4 exists
qt=`command -v qmake`
# checking if cmake exists
cmake=`command -v cmake`
# checking if virtualenv exists
virtenv=`command -v virtualenv`
virtenv2=`command -v virtualenv2`

if [ "$pip_exi" == "" ] && [ "$pip2_exi" == "" ]
then
  echo "Error: please install python-pip or python2-pip, from your package manager"
  exit 0
fi
if [ "$python" == "" ] && [ "$python2" == "" ]
then
  echo "Error: please install python or python2, from your package manager"
  exit 0
fi
if [ "$cmake" == "" ]
then
  echo "Error: please install cmake, from your package manager"
  exit 0
fi
if [ "$virtenv" == "" ] && [ "$virtenv2" == "" ]
then
  echo "Error: please install python-virtualenv or python2-virtualenv, from your package manager"
  exit 0
fi
if [ "$qt" == "" ]
then
  echo "Error: please install qt4 or qt4-defaults, from your package manager"
  exit 0
fi


if [ "$1" == "--install" ]
then
  if [ -f requirements.txt ]
  then
    echo "##### Creating virtual enviroment #####"
    virtualenv --python=python2.7 installiation/ && source installiation/bin/activate
    echo "##### Installing packages from pip #####"
    pip install -r requirements.txt
    echo "##### Adding user to local printers group #####"
    if [ "`groups | grep lp`" == "" ]
    then
      sudo usermod -a -G lp $(whoami)
      echo "##### All done #####"
      echo "%%% now you can do , python run.py and it should work %%%"
      read -p ">> System requires restart. Type yes to restart : " restart
      if [ "$restart" == "yes" ];then sudo shutdown -r now;fi
    fi
    echo "##### All done #####"
  else
    echo "Error: can not find the requirements text file"
  fi
elif [ "$1" == "--uninstall" ]
then
  echo "##### Uninstalling #####"
  if [ -d installiation/ ]
  then
    sudo rm -rf installiation/
    echo "##### All done #####"
  else
    echo "Error: enviroment not installed yet .."
  fi
elif [ "$1" == "--run" ]
then
  if [ -d installiation/ ]
  then
    source installiation/bin/activate
  else
    echo "Error: must --install enviroment first .."
    exit 0
  fi
  echo "##### Running FQM 0.2 #####"
  if [ -f run.py ]
  then
    python run.py
  else
    echo "Error: can not find FQM run.py"
  fi
else
  echo -e "\t --help : Usage \n"
  echo -e "\t\t $0 --install \t to install packages required"
  echo -e "\t\t $0 --uninstall \t to remove packages installed"
  echo -e "\t\t $0 --run \t to run FQM with the right settings"
  echo -e "\t\t $0 --help \t to print out this message"
fi

exit 0
