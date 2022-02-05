{ pkgs ? import <nixpkgs> { } }:
pkgs.stdenv.mkDerivation {
  name = "homepage";
  src = ./.;

  buildInputs = [ pkgs.hugo ];


  buildPhase = "hugo";

  installPhase = ''
    mkdir -p $out;
    mv public/* $out/;
  '';
}
