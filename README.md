# fx -- command line effects

This program provides various command line effects.

    #  Rename files "one", "two", and "three" to "2018.0105.one",
    # "2018.0105.two", and "2018.0105.three", respectively.

    $ fx -c "mv % 2018.0105.%" one two three

    # Rename files in the list, changing 'foo' in the filename to 'bar'

    $ fx -e s/foo/bar/ file1 file2 ... filen
