#!/bin/bash
# NOTE: this script will install FQM requirements and add your user into the
# printing group. this script purpose is to ease the process of installing, uninstalling
# FQM on Linux and MacOS. 

version="0.6"
pip_exi=`command -v pip`
python=`command -v python`
virtenv=`command -v virtualenv`
error1="Error: must --install enviroment first .."

if [ "$python" == "" ]
then
  echo "Error: please install python, from your package manager"
  exit 0
fi
if [ "$pip_exi" == "" ]
then
  sudo python3 -m ensurepip
fi
if [ "$virtenv" == "" ]
then
  sudo pip3 install vertualenv
fi


if [ "$1" == "--install" ]
then
  if [ -f requirements/dev.txt ]
  then
    echo "##### Creating virtual enviroment #####"
    virtualenv --python=python3 --system-site-packages installiation/ && source installiation/bin/activate
    echo "##### Installing packages from pip #####"
    pip install -r requirements/dev.txt
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
    rm -rf installiation/
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
    echo $error1
    exit 0
  fi
  echo "##### Running FQM $version #####"
  if [ -f run.py ]
  then
    python run.py
  else
    echo "Error: can not find FQM run.py"
  fi
elif [ "$1" == "--test" ]
then
  if [ -d installiation/ ]
  then
    pytest --count=2 -W ignore -vv tests/* --cov=./app
  else
    echo $error1
  fi
else
  echo -e "\t --help : Usage \n"
  echo -e "\t\t $0 --install \t to install packages required"
  echo -e "\t\t $0 --uninstall \t to remove packages installed"
  echo -e "\t\t $0 --run \t to run FQM with the right settings"
  echo -e "\t\t $0 --test \t to run FQM tests"
  echo -e "\t\t $0 --help \t to print out this message"
fi

exit 0
