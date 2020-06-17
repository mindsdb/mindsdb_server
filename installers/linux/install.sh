#!/bin/bash
echo "Please enter the path to your python (3.6+) interpreter:"
read python_path
export MDB_INSTALL_PYTHONPATH="$python_path"

echo "Please enter the path to your associate pip installation:"
read python_path
export MDB_INSTALL_PIPPATH="$python_path"

echo "Do you want us to install using the default parameters [Y] or should we go ahead and give you controll to tweak stuff during installation ? [Y/N]"
read default_install
export MDB_DEFAULT_INSTALL="$default_install"

export MDB_MAKE_EXEC="Y"
if [ "$EUID" -ne 0 ]; then
  install_as="user"
else
  install_as="global"
fi

if [ "$default_install" = "N" ] || [ "$default_install" = "n" ]; then
  if [ "$EUID" -ne 0 ]; then
      install_as="user"
      echo "You are currently installing Mindsdb for your user only, rather than globally. Is this intended ? [Y/N]"
      read approve
      if [ "$approve" = "N" ] || [ "$approve" = "n" ]; then
          echo "Please run the installer using sudo in front of the command"
          exit
      fi
    else
      install_as="global"
      echo "You are currently installing Mindsdb globally (as root), is this intended ? [Y/N]"
      read approve
      if [ "$approve" = "N" ] || [ "$approve" = "n" ]; then
          echo "Please run the installer as your desired user instead (without using sudo in front of it)"
          exit
      fi
  fi

  echo "Should we make an executable for mindsdb (in /usr/bin/ if installing as root or in your home directory if install as user)? [Y/N]"
  read make_exec
  export MDB_MAKE_EXEC="$make_exec"
fi



echo """
This might take a few minutes (dozens of minutes ?, no longer than half an hour, pinky promise).
Go grab a coffee or something and wait for the inevitable error log 99% of the way through

_,-||*||-~*)
(*~_=========\

|---,___.-.__,\

|        o     \ ___  _,,,,_     _.--.
\      -^-    /*_.-|~      *~-;*     \

 \_      _  ..                 *,     |
   |*-                           \.__/
  /                      ,_       \  *.-.
 /    .-~~~~--.            *|-,   ;_    /
|              \               \  | ****
 \__.--.*~-.   /_               |.
            ***  *~~~---..,     |
                         \ _.-.*-.
                            \       \

                             ..     /
                               *****
 """

INSTALLER_SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"${MDB_INSTALL_PYTHONPATH}" "$INSTALLER_SCRIPT_DIR"/install.py "$install_as" "$MDB_INSTALL_PYTHONPATH" "$MDB_INSTALL_PIPPATH" "$MDB_DEFAULT_INSTALL" "$MDB_MAKE_EXEC"
