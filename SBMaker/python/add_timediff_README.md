This is a one-shot program that takes in a ROOT file and adds a new
ntuple entry that contains the expected time since the last event of
its kind (in microseconds).

Before using, do these things in add_timediff.py
  - Change the bkgfiles variable to point to the directory containing which
    background you want to append times to
  - Change what you want the ntuple entrys name to be
  - Make sure that the ntuple entry you are adding in does not already
    exist in the file.  Otherwise, you will have to delete the ntuple
    entry from the tree first, then add it in.

