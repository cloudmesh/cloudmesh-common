with import <nixpkgs> {};

let

  # to update, run:
  # nix-prefetch-git git://github.com/NixOS/nixpkgs-channels refs/heads/nixpkgs-unstable
  src = pkgs.fetchFromGitHub {
    owner = "NixOS";
    repo = "nixpkgs-channels";
    rev = "7369fd0b51f4cfb4e47b19d4bdaf6809f099e747"; # 2017/04/24
    sha256 = "04d59cksi89q8s9wm4gw769yc488caq2bj7ifxmy7b8hjhchqwym";
  };

  pinned-pkgs = import src {};

in
pinned-pkgs
