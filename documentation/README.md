# documentation

This directory contains the PlanktoScope's documentation system. Documentation sources are in the `docs` subdirectory, while other files and subdirectories are used for building the documentation sources into a documentation website.

## Usage

### View the documentation

You can view the published documentation at the following URLs:

- <https://docs-edge.planktoscope.community/>: this shows the "edge" (i.e. development) version of documentation on the `master` branch of the main PlanktoScope repository at https://github.com/PlanktoScope/PlanktoScope . Note that this version probably contains errors and broken content, and it is not an official release of the documentation. This version of the documentation is hosted as a way for documentation maintainers to preview changes while working together across pull requests.
- <https://docs-beta.planktoscope.community/>: this shows the "beta" version of documentation on the `beta` branch of the main PlanktoScope repository. This version is shown to beta testers; it probably has problems, but it is more reliable than the "edge" version
- <https://docs.planktoscope.community>: this shows the "stable" version of documentation on the `stable` branch of the main PlanktoScope repository. This is the up-to-date version of PlanktoScope documentation which all PlanktoScope users should refer to as the official documentation website.

### Develop the documentation

First, use your favorite Git client (such as [Github Desktop](https://desktop.github.com/) or, if you already have some experience with Git, [GitKraken](https://www.gitkraken.com/)) to clone the PlanktoScope repository to your computer. For the rest of this development guide, we will assume you've cloned it to `/some/path/here/PlanktoScope` - you should replace that with the actual path where your local clone of the PlanktoScope repository is stored on  your computer.

#### Installing development tools

Explanation: We use [MkDocs](https://www.mkdocs.org/) to build documentation sources into a documentation website. We recommend running MkDocs on your computer while changing documentation sources so that you can preview the consequences of your changes. Because MkDocs is a Python tool, you will need to install it; and you will also need to install various MkDocs plugins used by our documentation site. We use [Poetry](https://python-poetry.org/) to manage the installation and versioning of MkDocs and MkDocs plugins so that everyone installs the exact same versions of all Python packages needed to build the documentation. We also use [Poe the Poet](https://poethepoet.natn.io/) to provide easy-to-run commands for developing the documentation.

You will need to install Python 3.8 or a more recent version of Python on your computer. If you don't have an appropriate version of Python installed on your computer, you can follow these instructions to install Python: <https://realpython.com/installing-python/>

Once you have Python, we recommend installing Poetry [using pipx](https://python-poetry.org/docs/#installing-with-pipx), as that is the easiest way to install Poetry. Please follow the instructions at https://pypa.github.io/pipx/installation/ to install pipx. Then run `pipx install poetry` in your terminal to install Poetry.

Now you can use Poetry to install the various Python tools and dependencies needed to build the documentation sources. In your terminal, change your current directory to the the `PlanktoScope/documentation` directory, and then run `poetry install --no-root`. For example (using our example path):

```
cd /some/path/here/PlanktoScope/documentation
poetry install --no-root
```

#### Making changes

To make changes, directly edit the files in the `docs` subdirectory using a text editor such as [Kate](https://kate-editor.org/), a Markdown editor such as [MarkText](https://github.com/marktext/marktext), or an IDE such as [Visual Studio Code](https://code.visualstudio.com/). You should make changes while live-previewing their consequences (see the next section, "Live-previewing changes" for instructions).

#### Live-previewing changes

Usually, you should edit the documentation sources (in `/some/path/here/PlanktoScope/documentation/docs`) while running a live preview of the documentation site. You can start the live preview server in your terminal using the following commands:

```
cd /some/path/here/PlanktoScope/documentation
poetry run poe preview
```

Then you can open the documentation website in your web browser at http://localhost:8000/ . Whenever you change a documentation source file, save your changes, and return to the web browser tab with the locally hosted documentation site, your changes will automatically appear within a few seconds!

#### Checking for errors

While changing the documentation source files, you should regularly check the documentation for errors. We provide some tools to help automate this process. You can run these tools in your terminal using the following commands:

```
cd /some/path/here/PlanktoScope/documentation
poetry run poe check
```

#### Locally building the documentation website

Usually you will not need to manually build a local copy of the documentation website, because we automate the process on GitHub as part of the process of deploying our documentation to a website on the internet. However, you can build a local copy of the documentation website using the following commands:

```
cd /some/path/here/PlanktoScope/documentation
poetry run poe build
```

(this also works for `preview`, `check`, and any other subcommands of `poe`)

#### Publishing your changes

To publish your changes, make a [pull request](https://github.com/PlanktoScope/PlanktoScope/pulls) on our GitHub repository with a branch titled `feature/docs-<description of your changes>` (e.g. `feature/docs-fix-broken-link` or `feature/docs-improve-assembly-instructions`), and configure the pull request to merge the branch into the `master` branch. Once we merge the pull request, your changes will be published to the "edge" version of our documentation website (see the above "View the documentation" section of this README for the URL of the "edge" version of our documentation website).
