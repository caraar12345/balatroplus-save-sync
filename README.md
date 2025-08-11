# Balatro+ Save Sync

A command-line tool to sync save files between Steam and Apple Arcade versions of Balatro+.

## Usage

The tool supports the following commands:

### Copy from Arcade to Steam
```bash
python main.py arcade-to-steam --arcade-save 1 --steam-save 1
```

### Copy from Steam to Arcade
```bash
python main.py steam-to-arcade --steam-save 1 --arcade-save 1
```

### Print Arcade Save Data
```bash
python main.py print-arcade --save 1
```

### Print Steam Save Data
```bash
python main.py print-steam --save 1
```

### Help
```bash
python main.py --help
python main.py <command> --help
```

## Arguments

- `--arcade-save {1,2,3}`: Arcade save slot number
- `--steam-save {1,2,3}`: Steam save slot number  
- `--save {1,2,3}`: Save slot number for print commands

All save slot numbers must be 1, 2, or 3.

## Examples

Copy save slot 2 from Arcade to Steam slot 1:
```bash
python main.py arcade-to-steam --arcade-save 2 --steam-save 1
```

Copy save slot 1 from Steam to Arcade slot 3:
```bash
python main.py steam-to-arcade --steam-save 1 --arcade-save 3
```

View the contents of Arcade save slot 2:
```bash
python main.py print-arcade --save 2
```