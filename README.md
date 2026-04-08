# Openreview tools

A simple set of scripts to extract data from Openreview 

## Dependencies
- [uv](https://github.com/astral-sh/uv) or
- [nix flakes](https://nixos.wiki/wiki/Flakes)

## Preparation

Copy `env.sample` to `.env` and fill in your OpenReview credentials:

`cp env.sample .env`

- `USERNAME`: your OpenReview account email
- `PASSWORD`: your OpenReview account password
- `VENUEID`: the OpenReview venue group id you want to query

`VENUEID` is the group id shown in the venue URL after `?id=`.

For example:

`https://openreview.net/group?id=example.org/Conference/2026/Workshop/MyWorkshop`

In that case, the `VENUEID` is:

`example.org/Conference/2026/Workshop/MyWorkshop`

## Scripts

### Export submissions 
`uv run src/ort/export_submissions.py`

Generates a CSV of all accepted papers (id, title, decision) with the list of authors (fullname, preferred email)

Thank you Stefano Mariani for contributing the base of this script.

> [!IMPORTANT]
> Openreview support team may have to enable preferred emails manually if the emails appear obfuscated.
> Contact support in this case <info@Openreview.net>
