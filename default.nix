with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "homepage";
  src = ./.;

  buildInputs = [ hugo ];

}
