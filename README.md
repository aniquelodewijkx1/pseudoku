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

    -t, --type (default std)
        std (standard), rare (currently WIP)

    -s, --size (default 9)
        4, 9, 16

For example, 
```
pseudoku -d hard -t std -s 9
```

If you do not include one of the required flags, don't worry! You will be prompted to enter these.

## Output
Sudoku puzzle ready for you to download!
