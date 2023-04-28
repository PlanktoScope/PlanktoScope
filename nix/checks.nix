{
  self,
  pre-commit-hooks,
  ...
}: system:
with self.pkgs.${system}; {
  pre-commit-check =
    pre-commit-hooks.lib.${system}.run
    {
      src = lib.cleanSource ../.;
      hooks = {
        alejandra.enable = true;
        nix-linter.enable = true;
      };
      settings = {
        nix-linter.checks = [
          "DIYInherit"
          "EmptyInherit"
          "EmptyLet"
          "EtaReduce"
          "LetInInheritRecset"
          "ListLiteralConcat"
          "NegateAtom"
          "SequentialLet"
          "SetLiteralUpdate"
          "UnfortunateArgName"
          "UnneededRec"
          "UnusedArg"
          "UnusedLetBind"
          "UpdateEmptySet"
          "BetaReduction"
          "EmptyVariadicParamSet"
          "UnneededAntiquote"
          "no-FreeLetInFunc"
          "no-AlphabeticalArgs"
          "no-AlphabeticalBindings"
        ];
      };
    };
}
