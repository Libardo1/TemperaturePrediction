## Andrew Taber ##

## Functionality:
## 1. Take keyboard input and open a file, read from file
## 2. Process the data in the file (i.e. organize data by grouping by location in a list indexed by date, then aggregating into dictionary of locations)
## 3. Perform analysis on data for each location* seperately hmmm
## 4. Put all the extended data together in a CSV array
## 5. Print array

## Specifics of #3:
## 1. Assuming weather is periodic to some extent, use discrete fourier transform to extract frequency data from input. 
## 2. Assuming a bit of randomness, simplify the frequency representation of data by using average over several days to represent data points. 
## 3. now we have the approximate frequencies that make up this signal, how do we predict what the coming signal will be??  

import sys
import numpy
import math

def get_location_dict(filename):
    csvfile=open(filename,'r')
    locations=dict()
    while csv.readline() != '':
        for i in range(1,len(csvfile.split(',')):
             if i not in locations.keys():
                   locations[i]=[int(csv.readline().split(',')[i])]
             else:
                   locations[i]+=[int(csv.readline().split(',')[i])
     return location
                       
def get_linear_regression(datelist):
     x = numpy.arange(len(datelist))
     y = numpy.array(datelist)
     A = numpy.vstack([x,numpy.ones(len(x))])
     m, c= numpy.linalg.lstsq(A,y)[0]
     import matplotlib.pyplot as plt
     plt.plot(x,y)
     plt.plot(x, m*x+c,'r')
     plt.show()
               

                           
