## PyTesting while multiprocessing?
### No worries! Read on!

This a demonstration of Python (py)testing while multiprocessing.

## Setup and run:

Setup is based on anaconda. I like to fix only the major packages, the rest, should be installed at their best version available.

    conda create -y --copy -n demo-mp python=3.9.2 pytest pytest-mock pytest-cov

That's it. Load the code in your IDE, configure it and run the tests, of course! Check the blog post for more descriptions!

## Coverage tests

Run More Run/Debug -> Run Pytest with Coverage

Note the lack of coverage in multiprocessing.

To have reports from multiprocessing (Will break the "regular" coverage)

1) Make .coveragerc in test folder with:

[run]
concurrency=multiprocessing
branch = True

Run it again from IDE. Now there is no coverage report shown!

Navigate where the IDE is saving the coverage files PyCharm: ~/.cache/JetBrains/PyCharmXXXX.Y/coverage

Make sure the conda env is active.
Run 

    coverage combine *.coverage.*; coverage xml

Now, back to IDE, Run -> Show Coverage Data -> Plus -> (navigate to xml)

Hint: If you want back the IDE coverage, disable the first line in .coveragerc

Enjoy!