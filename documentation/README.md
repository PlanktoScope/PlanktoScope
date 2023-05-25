# documentation

This directory contains the PlanktoScope's documentation system. Documentation sources are in the `docs` subdirectory, while other files and subdirectories are used for building the documentation sources into a documentation website.

## Usage

### Development

First, use your favorite Git client (such as [Github Desktop](https://desktop.github.com/) or, if you already have some experience with Git, [GitKraken](https://www.gitkraken.com/)) to clone the PlanktoScope repository to your computer. For the rest of this development guide, we will assume you've cloned it to `/some/path/here/PlanktoScope` - you should replace that with the actual path where your local clone of the PlanktoScope repository is stored on  your computer.

#### Installing development tools

We use [MkDocs](https://www.mkdocs.org/) to build documentation sources into a documentation website. We recommend running MkDocs on your computer while changing documentation sources so that you can preview the consequences of your changes. Because MkDocs is a Python tool, you will need to install it; and you will also need to install various MkDocs plugins.

We use [Poetry](https://python-poetry.org/) to manage the installation and versioning of MkDocs and MkDocs plugins so that everyone installs the exact same versions of all Python packages needed to build the documentation. We also use [Poe the Poet](https://poethepoet.natn.io/) to provide easy-to-run commands for developing the documentation. You will need to install Python 3.8 or a more recent version of Python on your computer. If you don't have an appropriate version of Python installed on your computer, you can follow these instructions to install Python: https://realpython.com/installing-python/

Once you have Python, we recommend installing Poetry [using pipx](https://python-poetry.org/docs/#installing-with-pipx), as that is the easiest way to install Poetry. Please follow the instructions at https://pypa.github.io/pipx/installation/ to install pipx. Then run `pipx install poetry` in your terminal to install Poetry.

Now you can use Poetry to install the various Python tools and dependencies needed to build the documentation sources. In your terminal, change your current directory to the the `PlanktoScope/documentation` directory, and then run `poetry install --with docs`. For example (using our example path):
```
cd /some/path/here/PlanktoScope/documentation
poetry install --with docs
```

#### Live development

Usually, you should edit the documentation sources (in `/some/path/here/PlanktoScope/documentation/docs`) while running a live preview of the documentation site. You can start the live preview server in your terminal using the following commands:
```
cd /some/path/here/PlanktoScope/documentation
poetry run poe preview
```

Then you can open the documentation website in your web browser at http://localhost:8000/PlanktoScope/ . Whenever you change a documentation source file, save your changes, and refresh the corresponding page in your browser, your changes will appear!

#### Check for errors

#### Locally build the documentation website

Usually you will not need to manually build a local copy of the documentation website, because we automate the process on GitHub as part of the process of deploying our documentation to a website on the internet. However, you can build a local copy of the documentation website using the following commands:
```
cd /some/path/here/PlanktoScope/documentation
poetry run poe build
```

If you really don't want to change your current working directory to `/some/path/here/PlanktoScope/documentation`, you can instead run the following command:
```
poetry -C /some/path/here/PlanktoScope/documentation run poe --root /some/path/here/PlanktoScope/documentation build
```

(this also works for `preview`, `check`, and any other subcommands)
