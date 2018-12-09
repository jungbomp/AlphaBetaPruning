# Alpha-Beta Pruning
This is an implementation of [alpha-beta pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning) on Python. Alpha-Beta pruning is an algorighm to reduce searching space on minimax searching tree. This program has a text file as an input parameter and generates result text file.


### The repository includes:
* Source code
* 5 basic test cases
* 50 big datasets

### Datasets
** Refer csci561_summer2018_hw1.pdf **
Input file
* DAY
Contains “today” or “yesterday” indicating which day the RPL was posted
* PLAYER
Contains either “R1” or “R2” indicating which roommate has next turn
* REGION PROFITABILITY LIST
Ordered list of tuples (Region_Identifier, Profit_Number).
* ADJACENCY MATRIX ROWS
The rows of the adjacency matrix representing the map.
<REGIONS PICKED SO FAR>
Comma separated list of regions picked so far. Will contain “*” if no activity yet.
<MAX DEPTH>
Number that determines the maximum depth of your search tree 
  
Output file
<NEXT REGION TO PICK> 
The next region the <PLAYER> should pick.
<UTILITY VALUE LIST>
In the case of a current RPL: A comma separated list of the utility of the <PLAYER> at the terminal nodes of the search tree (considering the maximum depth of <MAX DEPTH>) for the activity under the assumption that both players select moves maximizing their utilities.
In the case of a stale RPL: 
A comma separated list of the utility of the <PLAYER> at the next pick nodes under the assumption that both players select moves maximizing their utilities according to the heuristic function.
*FILE SHOULD HAVE NO BLANK LINE
  
### Building Environment
Python 2.7

### Compile & Run

```bash
$ python hw1cs561s18_alphabeta.py -i input1.txt
```

### Status

This is the first assignment of CSCI-561 Foundation of Artificial Intelligence, 2018 summer

Version 1.0

