# tululu.org books

Script for downloading books from science fiction section of tululu.org website.  
Script downloads book text, cover image and creates `books.json` file with book detailes and comments.

## [Go to library](https://paraigor.github.io/local_library/pages/index1.html)

### Installation

Python3 should already be installed. 
Use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Usage

Script accepts following command-line arguments:  
`--start_page` - start page number of science fiction section of the site. Default is 1.  
`--end_page` - end page number of science fiction section of the site. Default is number of last available page in the section.  
All books from specified pages will be downloaded. Page with `end_page` number included.
```
python parse_tululu_category.py --start_page 700
```
Books will be downloaded from all pages from 700 to last one.
```
python parse_tululu_category.py --start_page 700 --end_page 700
```
Books will be downloaded only from page 700.

`--dest_folder` - folder name to store book texts. Folder to store book cover images will be created with corresponding name `"{dest_folder}_img"`. Default is `"books"`.
```
python parse_tululu_category.py --dest_folder my_folder
```
`--skip_txt` - if specified, book texts willn't be downloaded.
```
python parse_tululu_category.py --skip_txt
```
`--skip_imgs` - if specified, book cover images willn't be downloaded.
```
python parse_tululu_category.py --skip_imgs
```
If no arguments will be specified, default values will be applied.

After library is downloaded, you can visit it locally on your computer. For this, just doubleclick on file `index1.html` from `pages` folder.

### Project Goals

This code was written for educational purposes as part of an online course for web developers at [dvmn.org](https://dvmn.org/). 
 
