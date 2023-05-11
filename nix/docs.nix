{
  mkdocs,
  python3,
}: let
  mkdocsOutput = mkdocs.build {
    src = ../.;
    siteDir = "site";
  };
in {
  package = python3.pip.buildPackages rec {
    mkdocs = mkdocsOutput;
  };
}
