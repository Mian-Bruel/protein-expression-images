# Protein-Expression-images
Protein expression images project for Problem Classes I
## Streamlit preview
[Streamlit link](https://protein-expression-images.streamlit.app/)

<img width=700 src="https://github.com/Mian-Bruel/protein-expression-images/assets/35274379/4c486e2a-dd57-429f-9cbc-5039b46a4e2a">

### Code Style

This repository uses pre-commit hooks with forced python formatting ([black](https://github.com/psf/black),
[flake8](https://flake8.pycqa.org/en/latest/), and [isort](https://pycqa.github.io/isort/)):

```sh
pip install pre-commit
pre-commit install
```

Whenever you execute `git commit` the files altered / added within the commit will be checked and corrected.
`black` and `isort` can modify files locally - if that happens you have to `git add` them again.
You might also be prompted to introduce some fixes manually.

To run the hooks against all files without running `git commit`:

```sh
pre-commit run --all-files
```
