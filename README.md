# bandit-multi-format

Provides a `multi` output formatter for Bandit that writes the same Bandit report in multiple formats (e.g. `json`, `txt`, `xml`). This is a small solution for https://github.com/PyCQA/bandit/issues/447.

## Purpose

When you want Bandit to produce multiple output formats from a single run, the `multi` formatter will call the configured Bandit formatters and write one output file per format.

## Install

Install from PyPI in your Bandit environment:

```bash
pip install bandit-multi-format
```

In case of using pipx to manage Bandit installation, you can inject the package into the existing Bandit pipx environment:

```bash
pipx inject bandit bandit-multi-format
```


## Usage

The `multi` formatter requires one environment variable to be set:

- `BANDIT_MULTI_FORMATS` (required): comma-separated list of Bandit formatter names to invoke (for example: `json,txt`).

Optional environment variable:

- `BANDIT_MULTI_OUTPUT_DIR` (optional): path to a directory where all outputs will be written. If not set, the formatter attempts to determine an output directory from Bandit's output file object (for example, when Bandit is run with `-o /path/to/outfile` it will use that file's parent directory). If neither is available, the formatter raises an error asking you to set `BANDIT_MULTI_OUTPUT_DIR`.

Notes:

- The special format name `multi` cannot be used inside `BANDIT_MULTI_FORMATS` (the package blocks it to avoid recursion).
- Output files are written as `bandit_output.<format>` (for example: `bandit_output.json`, `bandit_output.txt`) in the chosen output directory.

Example usage (write JSON and TXT outputs to `./bandit_outputs`):

```bash
export BANDIT_MULTI_FORMATS="json,txt"
export BANDIT_MULTI_OUTPUT_DIR="./bandit_outputs"
bandit -r path/to/project -f multi
```

If you prefer to let the formatter infer the output directory from Bandit's `-o` option, provide an output file when running Bandit:

```bash
export BANDIT_MULTI_FORMATS="json,txt"
bandit -r path/to/project -f multi -o ./reports/bandit_report.out
# This will create ./reports/bandit_output.json and ./reports/bandit_output.txt
```
Warning about using `-o`:

- The directory for the `-o` file must exist beforehand — Bandit will not create parent directories for the output file.
- Using `-o` can be confusing with the `multi` formatter because Bandit itself will open (and typically create/truncate) the `-o` file before formatters run. That means an empty file may be created at the `-o` path. In some cases this results in an extra empty file unless the `-o` filename matches what a formatter would write itself.

In practice: if you want clean outputs in a specific folder, it's often simpler to set `BANDIT_MULTI_OUTPUT_DIR` to the desired directory instead of relying on `-o`.

If you run Bandit without `-o` and without setting `BANDIT_MULTI_OUTPUT_DIR`, the `multi` formatter will raise an error and ask you to set `BANDIT_MULTI_OUTPUT_DIR`.

## Examples and troubleshooting

- Make sure each format listed in `BANDIT_MULTI_FORMATS` is a valid Bandit formatter available in your environment. The `multi` formatter will skip formats it cannot load and log errors.

## Implementation notes

- See `src/bandit_multi_format/__init__.py` for details: the formatter loads Bandit's registered formatters and calls each one, creating `bandit_output.<fmt>` files in the chosen directory.
