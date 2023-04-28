{self, ...}: system:
with self.pkgs.${system};
  mkShell {
    name = "planktoscope";
    nativeBuildInputs =
      [
        # Development
        editorconfig-checker
        pre-commit
        python-language-server
        python37
        python38
        python39
        python310Full
        python311
        yaml-language-server
        nodePackages.node-red
      ]
      ++ lib.optionals (pkgs.hostPlatform.system == "x86_64-linux") [
        vscodium-fhs
        eagle
      ]
      ++ [
        # Linter
        git
        yamllint

        # Nix
        alejandra
        nix
        nix-linter
        rnix-lsp

        # Service
        mosquitto

        # Misc
        reuse
      ];
    shellHook = ''
      ${self.checks.${system}.pre-commit-check.shellHook}
      pip install --upgrade pip hatch
      hatch env create dev
    '';
  }
