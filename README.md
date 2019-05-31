# Test_work
find similar images

The program consists of 2 parts: 
  1st detects identical and modified images (works very fast),
  2nd detects similar images (works slower)
  
The idea of 1st part:
  1) Switch color palette to gray shades and resize to 8*8 px image
  2) Calculate the value of avarage colour of pixels on picture
  3) Paint each pixel black or white whether it`s darker or lighter
    than the avarage color
  4) Create a hash code of the image by reading pixels row by row and
    putting 0 for white and 1 for black color
  5) Comparison between images lies in finding Hamming distance between 
    2 hash codes. 0 distance <==> identical; distance є [1,5] - modified
    (the values were defined after the test on dev_dataset)
    
 The idea of 2nd part:
  1) Use FAST method to detect key points of the image with N=12, 
    radius=3, t=90. Parameters N and t were defined after the 
    test on dev_dataset and considered as the most optimal.
  2) Firstly, check number of key points between 2 images. If the 
    images are similar, their kp number is not deviated
    significantly. Than find key points related to same fragments
    of the picture. This is done by analyzing the area next to the 
    key point. It was tested that the best way is to define area as
    a square 9*9px with key point in the center. Afterwards we 
    compare these squares in the same way as int the 1st part of the
    program. It is accaptable that the Hamming distance between 2 key
    points, that refer to the same fragment on 2 pictures, is between
    [0;3]. The best matching has the lowest Hamming distance.
  3) Images are than defined as similar if the number of common keypoints
    is not lower than a certain fraction out of avarage number of keypoints
    on both images.
