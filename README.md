# MP4andMP3Converter

if the following error occurs do the following
### 1.Go to your pythons file location
### 2.Locate the python Library pytube
### 3.Open the cipher.py
### 4.Scroll down to line 272 and 273
### 5.Delete the content of these 2 lines ( 272 and 273 ) and replace them with the following:
~~~python
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
~~~
