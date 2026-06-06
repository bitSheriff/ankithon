{
  description = "Convert markdown documents to Anki flashcards";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      utils,
    }:
    utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3;

        # Package genanki custom as it is not in nixpkgs
        genanki = python.pkgs.buildPythonPackage rec {
          pname = "genanki";
          version = "0.13.1";
          format = "wheel";

          src = pkgs.fetchurl {
            url = "https://files.pythonhosted.org/packages/af/7e/6c74ea7aaf2a36fd7df281267fade72e1f06ed1e44315bd77af2c6f82800/genanki-0.13.1-py3-none-any.whl";
            hash = "sha256-ZbWUNACFiKEhO5QEdNGsqMyoMkOvb8DiYgC1YO/k2eM=";
          };

          propagatedBuildInputs = with python.pkgs; [
            cached-property
            chevron
            frozendict
            pyyaml
          ];
        };

        ankithon = python.pkgs.buildPythonApplication {
          pname = "ankithon";
          version = "0.1.0";
          src = ./.;

          format = "other";

          propagatedBuildInputs = [
            genanki
            python.pkgs.markdown2
          ];

          dontBuild = true;

          installPhase = ''
            runHook preInstall
            mkdir -p $out/bin
            echo "#!/usr/bin/env python" > $out/bin/ankithon
            cat main.py >> $out/bin/ankithon
            cp -r src $out/bin/src
            chmod +x $out/bin/ankithon
            runHook postInstall
          '';

          meta = {
            description = "Convert markdown documents to Anki flashcards";
            homepage = "https://github.com/nx10/ankithon";
            license = pkgs.lib.licenses.mit;
          };
        };

        ankithon-compiled =
          let
            libPath = pkgs.lib.makeLibraryPath [
              pkgs.zlib
              pkgs.sqlite
              pkgs.stdenv.cc.cc.lib
            ];
          in
          pkgs.stdenv.mkDerivation {
            pname = "ankithon-compiled";
            version = "0.1.0";
            src = ./.;

            dontStrip = true;

            nativeBuildInputs = [
              pkgs.gcc
              pkgs.makeWrapper
              (python.withPackages (ps: [
                genanki
                ps.markdown2
                ps.nuitka
              ]))
            ];

            buildPhase = ''
              python -m nuitka \
                --standalone \
                --onefile \
                --include-package=src \
                --output-dir=build \
                main.py
            '';

            installPhase = ''
              mkdir -p $out/bin
              cp build/main.bin $out/bin/.ankithon-wrapped
              makeWrapper $out/bin/.ankithon-wrapped $out/bin/ankithon \
                --prefix LD_LIBRARY_PATH : "${libPath}"
            '';
          };
      in
      {
        packages.default = ankithon;
        packages.compiled = ankithon-compiled;

        apps.default = {
          type = "app";
          program = "${ankithon}/bin/ankithon";
        };
        apps.compiled = {
          type = "app";
          program = "${ankithon-compiled}/bin/ankithon";
        };

        devShells.default = pkgs.mkShell {
          packages = [
            (python.withPackages (ps: [
              genanki
              ps.markdown2
              ps.nuitka
            ]))
            pkgs.gcc
            pkgs.uv
          ];
        };
      }
    );
}
