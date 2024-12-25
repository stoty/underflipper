## About Underflipper

Underflipper is a script to convert the downloadable Warhammer Underworlds warband rules PDFs to 
a format that is fit for printing as a two-sided document ready for cutting and play.

## Getting Started

Underflipper is available as a Python project on GitHub.

### Prerequisites

To run Underflipper, you need a recent Python 3 environment.

#### Linux

Your distribution should already provide python 3.
If it is not currently installed, use your package manager to install it, i.e.

		apt-get install python3

#### Windows

Follow the [instructions](https://docs.python.org/3/using/windows.html)

#### MacOS

Follow the [instructions](https://docs.python.org/3/using/mac.html)

### Installation

#### Download

First, you need to download the project files.

If you have git installed, you may use the git command

		git clone https://github.com/stoty/underflipper.git

otherwise download the [ZIP archive](https://github.com/stoty/underflipper/archive/refs/heads/main.zip) and extract it.

#### (Optional) Create a virtual environment

Use your preferred method to create a virtual environment.
If you don't know what that it, it is safe to skip this step.

#### Install dependencies

Underflipper uses PyMuPDF for PDF manipulation. To install it, change to the project directory, and run the

		pip install -r requirements.txt

command.

## Usage

Download the warband rules PDF from https://www.warhammer-community.com/en-gb/downloads/warhammer-underworlds/
Note that currently only the single-warband PDFs are supported.

Open a terminal (Command Prompt or Powershell on windows), and run the script.
The first argument is the path to the original warband rules PDF, the second is the the path where the reformatted PDF will be created.
For simplicity, you may copy the PDF to the script directory, to avoid having to specify the full path names:

		python3 underflipper.py whuw_warband_sepulchral_guard_cards_download_eng_11-xax8ny92p9.pdf sepulchral_twosided.pdf

The resulting PDF should be printed in two sided mode (flip on long edge).
Enable automatic rotation, and disable page resizing when printing.
For printers without automatic duplex printing, the driver usually provides an option for manual two-sided printing.

### Calibrating the vertical offset

Some printers do not position the print area exactly, and which is not issue in most cases, but may cause the
two sides of the cards to not match up. A third option can be specified to correct for this skew.

Print the two-sided PDF on plain paper, then hold the paper towards a light source, and check if the prints on
the two sides align.

If not, then measure the skew and convert it to points (1/72th of an inch), and specify it as a third parameter.
positive values move the back side towards the top of the page, negative values towards the bottom of the page.

If necessary, iterate until the two sides of the prints cover each other perfectly.

The following example shows how to compensate for the back side being skewed 1.5mm (4.25pt) towards the bottom:

		python3 underflipper.py whuw_warband_sepulchral_guard_cards_download_eng_11-xax8ny92p9.pdf sepulchral_twosided.pdf -4.25

### Printing

For best results, use card stock.
See the recommended printer settings above.

## Contributing

Use GitHub issues to report problems or suggestions, and submit GitHub PRs for fixes and improvements

## License

Distributed under the GNU Affero General Public License.
See `LICENSE.txt` for more information.
