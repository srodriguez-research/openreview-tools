
{
  description = "Python dev environment with uv";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        python = pkgs.python311; # change if needed
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pkgs.uv
            pkgs.git
            pkgs.curl
            pkgs.zsh
          ];

          shellHook = ''
            echo "Python dev environment with uv"
            echo "Python: $(python --version)"
            echo "uv: $(uv --version)"

            # Optional: auto-create venv if not present
            if [ ! -d ".venv" ]; then
              echo "Creating virtual environment with uv..."
              uv venv
            fi

            source .venv/bin/activate
            exec zsh
          '';
        };
      });
}

