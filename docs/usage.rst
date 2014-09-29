========
Usage
========

Config file
-----------

First, you need to have a config file.  The easiest way to make a config file is to use the ``-g`` or ``--mkconfig`` option::

    shardgather -g > config.ini

Edit the config file to plug in the server info such as server host, username and so on.


Prepare input
-------------

Then, you can run ``shardgather`` and provide the SQL in a file::

    shardgather -c config.ini /path/to/query.sql

You may also instruct ``shardgather`` to read the query from standard input::

    shardgahter -c config.ini -

You may type the query directly into the console, and ``Ctrl+D`` to terminate input and send the query to ``shardgather``


Gather output
-------------

The result of ``shardgather`` is printed to standard out.  If you wish to store the output to a file, redirect ``stdout`` to a file::

    shardgather -c config.ini foo.sql > result

