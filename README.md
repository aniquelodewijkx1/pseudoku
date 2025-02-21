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

<div style="text-align: center;">
  <img src="https://raw.githubusercontent.com/aniquelodewijkx1/pseudoku/main/images/regular_hard_16x16.png" alt="regulat hard 16x16" width="250">
</div>

```
pseudoku -d easy -t hypergrid -s 9
```

<div style="text-align: center;">
  <img src="https://raw.githubusercontent.com/aniquelodewijkx1/pseudoku/main/images/hyper_easy_9x9.png" alt="hyper easy 9x9" width="250">
</div>


If you do not include one of the required flags, don't worry! You will be prompted to enter these.

**Note** if you create a hyper sudoku on a 4x4 puzzle, the values in the hypergrid will be the only empty ones,
or else a single solution is mathematically impossible. 

## Output
Sudoku puzzle will pop up in a new interactive window.
After entering values you can press 'Check' and see if any entries are incorrect.
