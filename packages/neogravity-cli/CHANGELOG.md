# Changelog

## 4.1.0

- Rewrote the scaffold template: it is now generic. Version 4.0.0 shipped a
  personal task list, local file paths and project notes that did not belong in a
  public package. **Please upgrade and stop using 4.0.0.**
- Removed the `fs-extra` dependency. The CLI now has zero dependencies.
- `init` never overwrites existing files, supports `--yes`, `--dir` and `--dry-run`.
- Added tests (`npm test`) and an MIT `LICENSE` in the package.
- Replaced the large "operating system" description with a plain one.
- The template no longer creates `projects.json` or `scripts/`.

## 4.0.0

First public release. Deprecated.
