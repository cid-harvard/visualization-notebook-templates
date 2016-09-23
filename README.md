# Visualization Notebook Templates
A set of iPython notebooks that can be used to generate some of the most common
atlas-style interactive visualizations with any old dataset, and also to be
able to dump them as embeddable html snippets.

# Setup (10-15 minutes - one time)

You need Python 2.7 or 3.x, latter preferred. If you don't already have it, an
easy way to get it is to install
[Anaconda](https://www.continuum.io/downloads), a premade bundle of python and
a lot of scientific computing packages that installs easily on many platforms.

Plus some python packages:
- Jupyter (formerly called IPython Notebook). If you install Anaconda, it'll
  come with it. Otherwise, you can install the package named `jupyter`.
- Pandas - for data analysis and munging formats. If you install Anaconda,
  it'll come with it. Otherwise, install `pandas`.
- Optionally, linnaeus. This is a package that has data on classification
  systems we commonly use, like HS. For this, instead of the package name, use
  `git+https://github.com/cid-harvard/classifications.git@v0.0.66#egg=linnaeus`
  when installing with pip. Find out more about this package
  [here](https://github.com/cid-harvard/classifications/).

To install these packages you should do `pip install <packagename>` in a
terminal. For terminal basics, check out [this
tutorial](http://lifehacker.com/5633909/who-needs-a-mouse-learn-to-use-the-command-line-for-almost-anything).
Replace `pip` with `pip3` if you are using python3. On linux or OSX, if it
complains about permissions, add `sudo -H` to the beginning of the command.
Finally, optionally and as an advanced feature, you can also use [Virtual
Environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/) if you
don't want to install packages globally and instead keep packages for each
project separate.

# Running the notebooks in Jupyter

Note: Unfortunately you can't just double-click a file and get it to launch
jupyter, you have to do it in this order.

1. *Copy the notebooks to your computer*: To do that, scroll to the top of the
   page and hit the big green "Clone or Download" button. If you don't know how
   to use git, you can just hit the "Download Zip" button. Otherwise, feel free
   to do whatever works. You can place this directory wherever you want.

2. *Run Jupyter*:  To make your life easier, you probably want to launch
   Jupyter from the terminal in the directory you downloaded this repository
   to. (As a reminder, you can read about using the terminal
   [here](http://lifehacker.com/5633909/who-needs-a-mouse-learn-to-use-the-command-line-for-almost-anything)).
   After you've used `cd` to get to the directory you copied the stuff to, you
   just run `jupyter notebook`.

   Anaconda has its own way of launching jupyter too, in that case you can use
   the file browser that pops up to navigate to the directory you downloaded
   the notebooks to.

3. *Load the notebooks*: Then, your browser will pop up a new window with a
   file browser, and you can click into the notebook you like. Start with
   Tutorial.ipynb


# Viewing notebooks on the web
Github has some functionality to view the notebooks (but not run them) on the
web, so you can see what's in them. Unfortunately it's bad at rendering the
actual visualizations themselves. What you can do is go to
[nbviewer](http://nbviewer.jupyter.org/) and paste in the url and it should
work fine.

# Do I need the whole directory?
No. If you want to use this in another project, you can keep only the bits and
pieces you need. You need `modules/d3plus2.py` for the python code that
generates the visualizations. You need the network .json files from the
`classifications` directory if you're using network visualizations and aren't
using your own.
