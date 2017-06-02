{ pkgs ? import ./nixpkgs.nix
}:

with pkgs;

let
  pyEnv = python27Full.withPackages (self: with self; [
    pip
    virtualenv
  ]);

  systemDeps = [
  ];

  buildInputs = [pyEnv] ++ systemDeps;

in

stdenv.mkDerivation {
  name = "cloudmesh_common_env";
  buildInputs = buildInputs;
  shellHook = ''
    # https://github.com/pikajude/darwinixpkgs/blob/master/doc/languages-frameworks/python.md
    # fixes: ZIP does not support timestamps before 1980
    export SOURCE_DATE_EPOCH=$(date +%s)

    export SSL_CERT_FILE=${cacert}/etc/ssl/certs/ca-bundle.crt
    test -d venv || virtualenv venv
    source venv/bin/activate

    # pip install -r requirements.txt
  '';
}
