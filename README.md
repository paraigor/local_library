# tululu.org books

Script for downloading books from tululu.org website.

### Installation

Python3 should already be installed. 
Use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Usage

Script accepts two command-line arguments, `start_id` and `end_id`, start and end IDs of book for range of book being downloaded.
```
python tululu.py 20 30
python tululu.py
```
If no arguments provided, books with IDs from 1 to 10 will be downloaded.

### Project Goals

This code was written for educational purposes as part of an online course for web developers at [dvmn.org](https://dvmn.org/). 
 
