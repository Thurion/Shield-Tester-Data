# Shield Tester Data

## How to use

1. Clone this repository `git clone`
2. Update git submodules
    ```
    git submodule init FDevIDs
    git submodule update FDevIDs
    git submodule init coriolis-data
    git submodule update coriolis-data
    ```
3. Run `create_data_file.py` in Python 3
4. Copy or move generated `data.json` to [Python port of D2EA's Shield Tester](https://github.com/DownToEarthAstronomy/D2EA_Shield_tester)