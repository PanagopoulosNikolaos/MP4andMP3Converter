# MP4andMP3Converter

if this error occurs ["An error occurred for path: get_throttling_function_name: could not find match for multiple"] do the following
### 1.Go to your pythons file location
### 2.Locate the python Library pytube
### 3.Open the cipher.py
### 4.Scroll down to line 272 and 273
### 5.Delete the content of these 2 lines ( 272 and 273 ) and replace them with the following:
~~~python
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
~~~
![mp3andmp4converter](https://github.com/user-attachments/assets/8328d93b-bb02-4d17-b45c-74fbf38e3d3f)


#Note:
~~~text
Keep in mind that this program download's Videos at the highest resolution available.
If the storage is limited please refrain from downloading videos with this program!
~~~
## Next update will include a resolution selection drop-down menu.
