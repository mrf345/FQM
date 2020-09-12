#!/bin/bash

pip_exi=`command -v pip3.7`
python=`command -v python3.7`
virtenv=`command -v virtualenv`
error1="Error: must --install enviroment first .."

if [ "$python" == "" ]
then
  echo "Error: please install python 3.7, from your package manager"
  exit 0
fi
if [ "$pip_exi" == "" ]
then
  sudo python3.7 -m ensurepip
fi
if [ "$virtenv" == "" ]
then
  sudo pip3.7 install virtualenv
fi


source ./app/env_vars.py


if [ "$1" == "--install" ]
then
  if [ -f requirements/dev.txt ]
  then
    echo "##### Creating virtual enviroment #####"
    virtualenv --python=python3.7 --system-site-packages installiation/ && source installiation/bin/activate
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
  echo "##### Running FQM $VERSION #####"
  if [ -f run.py ]
  then
    python run.py "${@:2}"
  else
    echo "Error: can not find FQM run.py"
  fi
elif [ "$1" == "--test" ]
then
  if [ -d installiation/ ]
  then
    source installiation/bin/activate
    rm -rf tests/__pycache__/
    if [ -z "$2" ]
    then
      python -m flake8 app/**/**/** tests/**/**/** && python -m pytest --count=2 -vv tests/*/* --cov=./app
    else
      python -m flake8 app/**/**/** tests/**/**/** && python -m pytest --count=$2 -vv tests/*/* --cov=./app
    fi
  else
    echo $error1
  fi
elif [ "$1" == "--migration" ]
then
  if [ -d installiation/ ]
  then
    source installiation/bin/activate
    python -c "p='app/__init__.py'; f=open(p, 'r'); c=f.read().replace('# app = bundle_app({', 'app = bundle_app({'); f=open(p, 'w+'); f.write(c); f.close()"
    flask db "${@:2}"
    python -c "p='app/__init__.py'; f=open(p, 'r'); c=f.read().replace('app = bundle_app({', '# app = bundle_app({'); f=open(p, 'w+'); f.write(c); f.close()"
  else
    echo $error1
  fi
else
  echo -e "$0 $1: Examples\n"
  echo -e "\t $0 --install \t to install packages required"
  echo -e "\t $0 --uninstall \t to remove packages installed"
  echo -e "\t $0 --run \t\t to run FQM"
  echo -e "\t $0 --test \t\t to run FQM tests"
  echo -e "\t $0 --migration \t to run FQM migration"
  echo -e "\t $0 --help \t\t to print out this message"
fi

exit 0
