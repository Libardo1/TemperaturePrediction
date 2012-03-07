'''
Created on Feb 11, 2012

@author: Andrew Taber
'''
## Workflow:
## 1. Take filename argument and open a file, read from file
## 2. Process the data in the file (i.e. organize data by grouping by location in a list indexed by date, then aggregating into dictionary of locations)
## 3. On each location's dataset, perform linear regression to find linear trend
## 4. To the linear trend add seasonal variations as learned from data of previous years
## 5. Aggregate location data into new dictionary containing predictions
## 6. Convert the dictionary into CSV format as in input

## Assuming temperature data has both a seasonal component and a linear trend (due to climate change), the better model would take both
## into account. We further assume that while there might be a linear trend in temperatures, the average distance of temperature from the 
## regression line as a function of seasonal position (where in the year a day falls) is approximately constant in the long term.
## As a result, we calculate the prediction for next year's data by first calculating where the linear regression predicts the temperature
## should be, and then taking into account seasonal factors by adding the expected distance from the regression line. The expected distance 
## is calculated as an exponentially weighted 

import sys
import numpy
import math
import matplotlib.pyplot as plt
    
def get_total_lines(filename):
    
    """Finds the total number of lines in a file given a filename as a parameter
    
    Input :: String
    
    Output :: Integer"""
    
    csvfile=open(filename,'r')
    numberOfLines=len(csvfile.readlines())
    csvfile.close()
    return numberOfLines

def get_location_dict(filename):
    
    """Converts CSV formatted file into a dictionary whose keys are column indices,
    and whose values are lists of values for a given column.
    
    Input :: CSV formatted file
    
    Output :: Dictionary whose keys are integers and whose values are lists
    
    TODO: Catch exceptions if dataset is not formatted correctly, is wrong size, etc."""
    
    print "Calculating database size..."
    filelength = get_total_lines(filename)
    print "Dataset has %i points" %filelength
    print "Beginning Calculations: \n"
        
    csvfile=open(filename,'r')
    locations={}
    nextline=csvfile.readline()
    
    current_line_number=0
    current_percent_completed=0
    
    print "Organizing dataset by location and date"
    while nextline != '':
        for i in range(1,len(nextline.split(','))):
            if i not in locations.keys():
                locations[i]=[int(nextline.split(',')[i])]
            elif i != len(nextline.split(','))-1:
                locations[i]+=[int(nextline.split(',')[i])]
            else:
                locations[i]+=[int(nextline.split(',')[i])] 
                #Move on to next line, update progress, log to user current percentage completed
                nextline = csvfile.readline()
                current_line_number+=1
                log_percent(current_percent_completed,math.floor(100*current_line_number/filelength))
                current_percent_completed=math.floor(100*current_line_number/filelength)       
    print "Dataset successfully organized! \n"
    
    return locations
                       
def log_percent(oldpercentage,newpercentage):
    if oldpercentage == newpercentage:
        pass
    else:
        print "Percent Completed: %i" %newpercentage
        
def get_linear_regression_coefficients(datelist):
    
    """Obtains the linear trend coefficient by a least squares method. 
    Takes a list of numbers as an input, and returns a tuple consisting of 
    the slope and intercept of the regression line.
    
    Input :: List of integers or floats
    
    Output :: Tuple of floats"""
    
    x = numpy.arange(len(datelist))
    y = numpy.array(datelist)
    A = numpy.vstack([x,numpy.ones(len(x))]).T
    m, c= numpy.linalg.lstsq(A,y)[0]
    return (m,c)

def get_regression_line(datelist):
    
    """Uses parameters found from get_linear_regression_coefficients to 
    get datapoints for the regression line.
    
    Input :: List of integers or floats
    
    Output :: numpy array of regression line fit to data"""
    
    x = numpy.arange(len(datelist))
    m, c = get_linear_regression_coefficients(datelist)
    
    return m*x+c

def get_previous_average_diff(datelist,date_number,width=10,weight_factor=.8):
    
    """Averages the values for previous years by taking **width** amounts of days
    from previous years approximately centered at **date_number** and averaging the
    distance between these values and the regression line at that time.
    The average from previous years is exponentially weighted, so older data gets much less weight. 
    
    Input :: Datelist - list of numbers; Date_number - a number signifying the position in the year of the
    date we're interested in; Width - number specifying how many days we should average over; 
    Weight_factor - number between 0 and 1 that changes how quickly we 'forget' about older data.
    
    Output :: Integer or float"""    

    t = date_number    
    reg_line = get_regression_line(datelist)
    difference_list = []
    
    while t < len(datelist):
        if t-width/2 < 0:
            difference = reg_line[t] - numpy.average(datelist[0:t+width/2])
            difference_list += [difference]
        elif t+width/2 > len(datelist):
            difference = reg_line[t] - numpy.average(datelist[t-width/2:])
            difference_list += [difference]
        else:
            difference = reg_line[t] - numpy.average(datelist[t-width/2:t+width/2])
            difference_list += [difference]    
        t+= 365 #Move on to same time next year
    
    weight_list = []
    for i in range(0,len(difference_list)):
        weight_list+= [weight_factor**-(i+1)]
        weight_list.reverse() #So more recent values get more weight
    
    difference_average = numpy.average(difference_list,weights=weight_list)
    return difference_average
    
def get_prediction(datelist,date_number):
    
    """Given a list of numbers and a number specifying the position of the date whose value we're interested in,
    returns the prediction of the value on that date
    
    Input :: Datelist - list of numbers; date_number - integer
    
    Output :: Float or integer"""
    
    reg_line = get_regression_line(datelist)
    previous_average = get_previous_average_diff(datelist,date_number)
    prediction = reg_line[date_number] + previous_average
    
    return prediction

def get_next_year_data(datelist):
    
    """Given a list of values, predict the values for a whole year
    
    Input :: List of numbers
    
    Output :: List of numbers"""
    
    new_year_values = []
    for t in range(1,366):
        new_year_values+= [get_prediction(datelist,t)]

    return new_year_values

def predict(filename,plot=False):
    
    """Given a filename, retrieve the value data from file and predict the next year's values
    for each location.
    
    Input :: String; Optional Boolean 
    
    Output :: Prints to STDOUT """
    
    prediction = {}
    location_dict = get_location_dict(filename)
    
    print "Beginning prediction algorithm: \n"
    for location_number, location_data in location_dict.iteritems():
        print "Calculating prediction for location number %i" %location_number
        prediction[location_number] = get_next_year_data(location_data)
    
    print "Prediction algorithm successfully terminated! \n"
    
    if plot:
        plt.plot(prediction[2])
        plt.show()
    
    to_csv_format(prediction)

def to_csv_format(location_dict):
     
    """Converts our dictionary formatted data into CSV format like the input file to Weather.py.
    Is the inverse of get_location_dict().
    
    Input :: Dictionary
    
    Output :: None (Writes to STDOUT)"""
    
    print "Writing CSV Output..."
    
    csv_string = ""
    
    for i in range(0,365): 
        Date_name= "2010-" + get_posix_date(i+1)
        csv_string+= Date_name + ',' #Print date as first entry to line
        csv_string+= write_csv_line(location_dict,i)
    
    print csv_string

def write_csv_line(dictionary,index):
    """Helper function to modularize the inversion process from dictionary to CSV file"""
    
    csv_line=''
    for i in range(1,len(dictionary.keys())):
        if i< len(dictionary.keys())-1:
            csv_line+= str(dictionary[i][index]) + ","
        else: 
            csv_line+= str(dictionary[i][index]) + "\n" 

    return csv_line

def get_posix_date(i):
    
    """Convert a number signifying position in the year into POSIX %M-%D format
    
    Input :: Integer
    
    Output :: String"""
    
    assert(type(i)==int)  
      
    if i < 10:
        i = "0%s"%i
    if i <= 31:
        return "01-%s"%i
    elif i <= 59:
        i= int(i)-31
        return "02-%s"%i
    elif i <= 90:
        i= int(i)-59
        return "03-%s"%i
    elif i <= 120:
        i= int(i)-90
        return "04-%s"%i
    elif i <= 151:
        i=int(i)-120
        return "05-%s"%i
    elif i <= 181:
        i=int(i)-151
        return "06-%s"%i
    elif i <= 212:
        i=int(i)-181
        return "07-%s"%i
    elif i <= 243:
        i=int(i)-212
        return "08-%s"%i
    elif i <= 273:
        i= int(i)-243
        return "09-%s"%i
    elif i <= 304:
        i= int(i)-273
        return "10-%s"%i
    elif i <= 334:
        i= int(i)-304
        return "11-%s"%i
    else:
        i= int(i)-334
        return "12-%s"%i

def test():
    #loc_dict=get_location_dict(sys.argv[1])
    #to_csv_format(loc_dict)   
    #plt.plot(get_regression_line(loc_dict[1]))
    #plt.plot(loc_dict[1])
    #plt.show()
    #print get_regression_line(loc_dict[1])
    #print len(get_regression_line(loc_dict[1]))
    predict(sys.argv[1],plot=True)

if __name__ == '__main__':
    predict(sys.argv[1])