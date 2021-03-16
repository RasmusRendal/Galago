{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/1af2af99ff354239b53bb9b5c9c689e236e06085.tar.gz") {}
}:
  pkgs.mkShell {
    #nativeBuildInputs = with pkgs; [ libstdcxx5 ];
    buildInputs = with pkgs; [ python38 python38Packages.pyside2 python38Packages.jedi python38Packages.pylint qt5.full ];
  }
