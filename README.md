# Openreview tools

A simple set of scripts to extract data from Openreview 

## Dependencies
- [uv](https://github.com/astral-sh/uv) or
- [nix flakes](https://nixos.wiki/wiki/Flakes)


## Scripts

### Export submissions 
`uv run src/org/export_submissions.py`

Generates a CSV of all accepted papers (id, title, decision) with the list of authors (fullname, preferred email)

Thank you Stefano Mariani for contributing the base of this script.

> [!IMPORTANT]
> Openreview support team may have to enable preferred emails manually if the emails appear obfuscated.
> Contact support in this case <info@Openreview.net>



