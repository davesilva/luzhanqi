Luzhanqi
======================

A Luzhanqi AI written for [CS4500](http://www.ccs.neu.edu/course/cs4500sp14/).

Authors
----------------------

David Silva: silva.davi@husky.neu.edu

Nathan Holmes: holmes.na@husky.neu.edu

Amat Cama: cama.a@husky.neu.edu

Feng-Yun Lin: lin.f@husky.neu.edu

Running Luzhanqi
----------------------

Open up the command line:

    cd <directory containing Luzhanqi>
    ./play4500 —go <n> —time/move <t>

    <n> is 1 or 2 depending on whether the player goes first
        or second (respectively)
    <t> is the time allowed per move in any of these formats:

        2s
        2.0s
        2000ms
        2000.0ms

Example:

    ./play4500 --go 1 --time/move 1.2s

says the player goes first and will be given 1.2 seconds per move.
