# 🍙 pseudoku
A sick sudoku generator.

## 🥢 Installation
```
pip install git+https://github.com/aniquelodewijkx1/sudoku.git
```

## 🍣 Usage
 You can run pseudoku from your cli with the following flags.
    
    -d, --difficulty (required)
        easy, medium, hard, extreme

    -t, --type (default standard)
        standard, hypergrid

    -s, --size (default 9)
        4, 9, 16

For example, 
```
pseudoku -difficulty hard -type standard -size 16
```
![alt text](https://https://github.com/aniquelodewijkx1/pseudoku/blob/main/images/hyper_easy_9x9.png)
```
pseudoku -d easy -t hypergrid -s 9
```
![alt text](https://github.com/aniquelodewijkx/pseudoku/blob/main/images/hyper_easy_9x9.png)

If you do not include one of the required flags, don't worry! You will be prompted to enter these.

**Note** if you create a hyper sudoku on a 4x4 puzzle, the values in the hypergrid will be the only empty ones,
or else a single solution is mathematically impossible. 

## Output
Sudoku puzzle ready for you to download!
