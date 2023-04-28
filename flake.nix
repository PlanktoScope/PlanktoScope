{
  description = "Nix PlanktoScope";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };

    flake-utils.url = "github:numtide/flake-utils";

    pre-commit-hooks = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  } @ inputs:
    flake-utils.lib.eachSystem ["x86_64-linux" "aarch64-linux"] (system: {
      devShells.default = import ./nix/shell.nix inputs system;
      checks = import ./nix/checks.nix inputs system;
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        config.allowAliases = true;
      };
    });
}
