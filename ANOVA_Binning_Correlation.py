"""
This script takes data from an excel sheet and performs ANOVA and correlation
on a set of data.  It also gives a framework to visualize the data and bins
the data in order to be fit for other statistical analyses in other software.

Author: Brian Andrews
"""

import sys
import math
import xlrd
from xlrd import open_workbook
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta

#*******************************************************************************
#Functions for data storage and statistical analysis

#function that copies the excel sheet to a table
def store(colnum, rownum, case, data, table = [[]]):
    numFromString = 0
    check = False
    for i in range(case): #loops traversing xlsx files
        for j in range(data):
            """if j == data-1:
                ycoord = abs(gety(mainSheet.cell_value(rownum+i, 11)))
                table[i,j] = ycoord
            elif j == data-2:
                xcoord = getx(mainSheet.cell_value(rownum+i, 11))
                if mainSheet.cell_value(rownum+i,2) == "OS":
                    xcoord = -1*xcoord
                table[i,j] = xcoord"""
            if j == data-1:
                table[i,j] = table[i,11]-table[i,10] #difference in pachy min and pachy apex
            elif j == data-2: #add spherical equivalence MRx error
                table[i,j] = table[i,7] + (table[i,8]/2) #cols 7 and 8 have spherical and cylindrical mrx data
            elif mainSheet.cell_value(rownum-1, colnum+j) == "DateOfBirth": #need to edit date of birth column
                date = datetime(*xlrd.xldate_as_tuple(mainSheet.cell_value(rownum+i, colnum+j), 0))
                dateStr = str(date) #change the date to a string
                table[i,j] = 2017 - strToFloat(dateStr)
            else:    
                #check if there are strings
                check = isinstance(mainSheet.cell_value(rownum+i,colnum+j), str)
                if check == False: #if entry is not a string (therefore, an int), add to table
                    table[i,j] = mainSheet.cell_value(rownum+i, colnum+j)
                if check == True: #if entry is a string
                    numFromString = strToFloat(mainSheet.cell_value(rownum+i, colnum+j)) #strip it and take first number 
                    table[i,j] = numFromString #add new float to table
                    check = False #make check False again so the loop works
    return table

#converts string to float and only takes first number as an argument
def strToFloat(dat):
    newNum = 0
    newStr = ""
    for i in range(len(dat)): #takes the number before the first space (want magnitude of strain not coordinates...for now)
        if dat[i] == ' ':
            break
        if (dat[i] == '-' and i != 0):
            break
        newStr += dat[i] #put the number into a new string
    newNum = float(newStr) #make it a float
    return newNum

def getx(dat):
    newNum = 0
    newStr = ""
    found = 0
    for i in range(len(dat)):
        if dat[i] == ',':
            break
        if found == 1:
            newStr += dat[i]
        if dat[i] == '(':
            found = 1
    newNum = float(newStr)
    return newNum

def gety(dat):
    newNum = 0
    newStr = ""
    found = 0
    for i in range(len(dat)):
        if dat[i] == ')':
            break
        if found == 1:
            newStr += dat[i]
        if dat[i] == ',':
            found = 1
    newNum = float(newStr)
    return newNum
        

#ANOVA test function between same column of each table cont[i] vs ect[i]
def anova(n, k,casesE, count, cont =[], ect=[]):
    #calculate the degrees of freedom
    dfBet = k-1
    dfWith = n-k
    #need to calculate the means of each group and grand mean of whole data set
    means = []
    for i in range(k+1):
        means.append(0)
    sumentries = 0 #variable to sum whole data set
    #loop to calculate means
    for j in range(len(cont)):
        means[0] += cont[j]
        sumentries += cont[j]
    for b in range(len(ect)):
        means[1] += ect[b]
        sumentries += ect[b]
    means[0] = means[0]/len(cont)
    means[1] = means[1]/len(ect) #at the end of the inner loop divide by number of cases to retrieve in group average
    means[2] = sumentries/n #whole sample mean

    #now calculate sum of the squares within and between
    sstot = 0 #sum of the squares of the difference between i and global mean
    sswith = 0 #sum of the squares of the difference beween i and mean of group k, summed over k groups
    for m in range(k):
        if m == 0:
            for b in range(len(cont)): #calculating the sum of the squares
                sstot += (cont[b]-means[2])*(cont[b]-means[2])
                sswith += (cont[b]-means[m])*(cont[b]-means[m])
        else:
            for b in range(len(ect)):
                sstot += (ect[b]-means[2])*(ect[b]-means[2])
                sswith += (ect[b]-means[m])*(ect[b]-means[m])
    ssbet = sstot - sswith #sum of squares between is the difference of the two values previously calculated
    F = ((ssbet*dfWith)/(sswith*dfBet)) #formula for F statistic
    #print(means,sswith, ssbet, F, dfBet, dfWith)
    print(F,dfBet,dfWith)


#function to make plots of two lists of data
def makeplot(colnum1, colnum2, numcase, ptitle, cont = [[]], ect = [[]]):
    plt.title(ptitle)
    plt.plot(cont[:,colnum1],cont[:,colnum2], 'b^', ect[:,colnum1],ect[:,colnum2],'r^')
    plt.show()

def average(array = []):
    sum1 = 0
    for t in range(len(array)):
        sum1 += array[t]
    average = sum1/len(array)
    return average

#make weird plot with averages of the two groups here
def makeplot1(colnum1, colnum2, numcase, ptitle, cont = [[]], ect = [[]], zer = [], on = []):
    y1 = average(ectasia[:,colnum2])
    y2 = average(control[:,colnum2])
    y3 = (y1 + y2)/2
    plt.title(ptitle)
    plt.plot(zer,cont[:,colnum2], 'b^', on,ect[:,colnum2],'r^')
    plt.axhline(y = y2, color='b', linestyle='-')
    plt.axhline(y = y1, color='r', linestyle='-')
    plt.axhline(y = y3, color='g', linestyle='-')
    plt.show()

#correlation calculation function
def Correlate(list1 = [], list2 = []): #LIST2 IS THE COMPANY CLASSIFICATION (EMPLOYEE NUM, CLIENT NUM, AGENCY TYPE, ETC.) ALWAYS
    #calculate different quantities individually
    sumlist1 = 0
    sumlist2 = 0
    sumlist1sq = 0
    sumlist2sq = 0
    productsum = 0
    counter = 0
    anothercounter = 0
    for x in range(len(list1)):
        if list2[x] != 0: #company needs to give this info for analysis
            counter = counter + 1
            sumlist1 = sumlist1 + list1[x]
            sumlist1sq = sumlist1sq + (list1[x]*list1[x])
    for x in range(len(list2)):
        if list2[x] != 0: #company needs to give this info for analysis
            sumlist2 = sumlist2 + list2[x]
            sumlist2sq = sumlist2sq + (list2[x]*list2[x])
    for x in range(len(list2)):
        productsum += list1[x]*list2[x]
        
    rnum = ((counter*productsum)-(sumlist1*sumlist2))
    rdem = math.sqrt(((counter*sumlist1sq)-(sumlist1*sumlist1))*((counter*sumlist2sq)-(sumlist2*sumlist2)))
    r = rnum/rdem
    return r

#calculates variance of original data set
def var(cases, array=[]):
    sum1 = 0
    average = 0
    sumsq =  0
    for g in range(len(array)): #calculate averages
        sum1 += array[g]
    average = sum1/len(array)
    print(average)

    for h in range(len(array)): #calculate average sum of squares
        sumsq += (array[h]-average)*(array[h]-average)
    var = sumsq/len(array)
    return var

#calculates variance of binned data using average of unbinned data
def binvar(bins, cases, ar1=[], ar2=[], ar3=[]):
    sum1 = 0
    average = 0
    sumsq =  0
    for g in range(cases): #calculate averages
        sum1 += ar3[g]
    average = sum1/cases

    for h in range(bins): #calculate average sum of squares
        sumsq += ar2[h]*(ar1[h]-average)*(ar1[h]-average)
    var = sumsq/cases
    return var

#function to create a 2D table for a histogram
def twodhist(cases, binloc1 = [], binloc2 = [], data1 = [], data2 = []):
    table = np.zeros((len(binloc1), len(binloc2)),float)
    for g in range(len(binloc1)):
        for t in range(len(binloc2)):
            for k in range(cases):
                if (data1[k] == binloc1[g] and data2[k] == binloc2[t]):
                    table[g,t] += 1
    #quick sum of components to check that all were accounted for.
    sum2 = 0
    for u in range(len(binloc1)):
        for o in range(len(binloc2)):
            sum2 += table[u,o]
    print(sum2)
    return table

#function of probability distribution
def calculateProb(msc, msp, mrx, pm):
    prob = .0193246*math.exp(-4.55044*((.242549*(mrx+3.87857)*(mrx+3.87857))+(8.92374*(mrx+3.87857)*(msc-.339693))+(87.6431*(msc-.339693)*(msc-.339693)))
                             -.917843*((73.33*(msp-2.47553)*(msp-2.47553))+(.00197544*(pm-523.829)*(pm-523.829)))-(.69495*(msp-2.47553)*(pm-523.829)))
    return prob

def calcProb2(mscOmrx, pmOmsp):
    prob = 0.15633474915053153*math.exp((-.00086144*(pmOmsp-212.301)*(pmOmsp-212.301))-(280.017*(mscOmrx+.10463)*(mscOmrx+.10463)))
    return prob

def calcProbSimp(msp, pm):
    prob = 0.011484952372992569*math.exp(-.91784*((73.3299*(msp-2.4755)*(msp-2.4755))+(.0019755*(pm-523.829)*(pm-523.829)))-(.69495*(pm-523.829)*(msp-2.4755)))
    return prob

def calcProbAgain(mrxs, mrxc, pm, pa, msp, maxsp, msc, maxsc, age, k):
    prob = 8.325471124810573*math.exp((-.009239243888*(age-37.1571)*(age-37.1571))+(-.04697817522*(k-48.744315)*(k-48.744315))+(-.57273898*(mrxc-1.0214)*(mrxc-1.0214))
                                      +(-13.9173237984*((14.981151*(maxsc-.2333)*(maxsc-.2333))+(-1.6434206*(maxsc-.2333)*(mrxs+3.87857))+(.144961596*(mrxs+3.87857)*(mrxs+3.87857))
                                                        +(-55.94898067*(maxsc-.2333)*(msc-.33969))+(6.6043644*(mrxs+3.87857)*(msc-.33969))+(84.9233277*(msc-.33969)*(msc-.33969))))
                                      +(-64.20269611714*((218.94605*(maxsp-3.0441428)*(maxsp-3.0441428))+(-1350.4925093*(maxsp-3.0441428)*(msp-2.475534))+(2170.4475597*(msp-2.475534)*(msp-2.475534))
                                                         +(16.436047*(maxsp-3.0441428)*(pa-527.2))+(-52.92238016*(msp-2.475534)*(pa-527.2))+(.3402*(pa-527.2)*(pa-527.2))+(-19.111674377*(maxsp-3.0441428)*(pm-523.828571))
                                                         +(61.8857407*(msp-2.475534)*(pm-523.828571))+(-.7899535*(pa-527.2)*(pm-523.828571))+(.460166*(pm-523.828571)*(pm-523.828571)))))
    return prob

def tru(msp, maxsp, pm, pa):
    prob = 217.763 * math.exp(-64.2027*((218.946*(maxsp-3.04414)*(maxsp-3.04414))+(-1350.492509*(maxsp-2.04414)*(msp-2.47553))+(2170.4475597*(msp-2.47553)*(msp-2.47553))+(16.43604725*(maxsp-3.04414)*(pa-527.2))+(-52.922380*(msp-2.475534)*(pa-527.2))+(.34204*(pa-527.2)*(pa-527.2))+(-19.1117*(maxsp-3.04414)*(pm-523.829))+(61.8857*(msp-2.47553)*(pm-523.829))+(-.7899535494*(pa-527.2)*(pm-523.829))+(.460166*(pm-523.829)*(pm-523.829))))
    return prob

def fal(msp, maxsp, pm, pa):
    prob = 17.771280856813565 * math.exp(-7.960617714236831*((537.3193963771747*(maxsp-2.912857)*(maxsp-2.912857))+(110.9519869*(maxsp-2.912857)*(msp-2.3621619))+(19.3312177899*(msp-2.3621619)*(msp-2.3621619))+(4.23299272958*(maxsp-2.912857)*(pa-543.471428))+(.5477626757*(msp-2.3621619)*(pa-543.471428))+(.3046880434026*(pa-543.47142857)*(pa-543.47142857))+(-19.121452*(maxsp-2.912857142)*(pm-541.5142857))+(-2.289060218*(msp-2.36216193)*(pm-541.5142857))+(-1.550425692*(pa-543.47142857)*(pm-541.5142857))+(2.00929360*(pm-541.5142857)*(pm-541.5142857))))
    return prob

#*******************************************************************************
#Main program begin
#Establish Initial Conditions Below

#Number of cases to be examined
numberOfCases = 70
numControl = 258
#Number of data points collected
TotalnumberOfDataPoints = 24 #total data including eye measurements
numberOfDataPoints = 6 #number of data points regarding strain

#column and row of excel sheet where necessary data is kept
#ignore headings and names/id/etc.
coln = 5
rown = 1

#******************************************************************************
#access control data
book = open_workbook('Control12_strain_fix.xlsx')
mainSheet = book.sheet_by_index(0)

#table to store control data
control = np.zeros((numControl, TotalnumberOfDataPoints), float)

#begin reading and storing the data from the excel sheet
control = store(coln, rown, numControl, TotalnumberOfDataPoints, control)

#close book and delete pointers
book.release_resources()
del book

#*******************************************************************************
#access ectasia data
book = open_workbook('Ectasia13_strain_fix.xlsx')
mainSheet = book.sheet_by_index(0)

#table to store ectasia data
ectasia = np.zeros((numberOfCases, TotalnumberOfDataPoints), float)

#begin reading and storing the data from the excel sheet
ectasia = store(coln,rown,numberOfCases,TotalnumberOfDataPoints, ectasia)

#close book and delete pointers
book.release_resources()
del book


#*******************************************************************************
#where ANOVA test script will go for comparing pre and post strain conditions
#loop through all of the tests using one function
for h in range(TotalnumberOfDataPoints): #do ANOVA test for each
    anova(numberOfCases+numControl, 2, numControl, h, control[:,h], ectasia[:,h])

#*******************************************************************************
#section for plotting strain variables vs MRx variables
#attempt to loop through the different options
#makeplot(0,6,numberOfCases,'',control,ectasia)

#array for titles
titles = ["Spherical MRx v Mean Strain Sim Outcome",
          "Cylindrical MRx v Mean Strain Sim Outcome",
          "Axis MRx v Mean Strain Sim Outcome",
          "Spherical MRx v Mean Strain Sim Change",
          "Cylindrical MRx v Mean Strain Sim Change",
          "Axis MRx v Mean Strain Sim Change",
          "Spherical MRx v Mean Strain PreTreatment",
          "Cylindrical MRx v Mean Strain PreTreatment",
          "Axis MRx v Mean Strain PreTreatment",
          "Spherical MRx v Max Strain Sim Outcome",
          "Cylindrical MRx v Max Strain Sim Outcome",
          "Axis MRx v Max Strain Sim Outcome",
          "Spherical MRx v Max Strain Sim Change",
          "Cylindrical MRx v Max Strain Sim Change",
          "Axis MRx v Max Strain Sim Change",
          "Spherical MRx v Max Strain PreTreatment",
          "Cylindrical MRx v Max Strain PreTreatment",
          "Axis MRx v Max Strain PreTreatment"]
i = 0
for w in range(1, numberOfDataPoints+1, 1): #traverse strain data
    for q in range(1, 4, 1):
        makeplot(w, q+numberOfDataPoints, numberOfCases,titles[i],control,ectasia)
        i+=1

#plotting all of the sph equivalence data
titlesSpEr = ["Spherical Equivalence v Mean Strain Sim Outcome",
          "Spherical Equivalence v Mean Strain Sim Change",   
          "Spherical Equivalence v Mean Strain PreTreatment",
          "Spherical Equivalence v Max Strain Sim Outcome",
          "Spherical Equivalence v Max Strain Sim Change",
          "Spherical Equivalence v Max Strain PreTreatment"]

for n in range(1,numberOfDataPoints,1):
    makeplot(n, TotalnumberOfDataPoints-1, numberOfCases, titlesSpEr[n-1], control, ectasia)

#plotting all of the pachy data (corneal thickness)
j = 0
titles2 = ["Pachy Min v Mean Strain Sim Outcome",
           "Pachy Max v Mean Strain Sim Outcome",
           "Pachy Min v Mean Strain Sim Change",
           "Pachy Max v Mean Strain Sim Change",
           "Pachy Min v Mean Strain Pretreatment",
           "Pachy Max v Mean Strain Pretreatment",
           "Pachy Min v Max Strain Sim Outcome",
           "Pachy Max v Max Strain Sim Outcome",
           "Pachy Min v Max Strain Sim Change",
           "Pachy Max v Max Strain Sim Change",
           "Pachy Min v Max Strain Pretreatment",
           "Pachy Max v Max Strain Pretreatment"]

for t in range(1, numberOfDataPoints+1, 1):
    for u in range(TotalnumberOfDataPoints-3, TotalnumberOfDataPoints-1):
        makeplot(t, u, numberOfCases, titles2[j], control, ectasia)
        j+=1

#plotting age data versus everything
titlesAge = ["Age v Mean Strain Sim Outcome",
           "Age v Mean Strain Sim Change",
           "Age v Mean Strain Pretreatment",
           "Age v Max Strain Sim Outcome",
           "Age v Max Strain Sim Change",
           "Age v Max Strain Pretreatment",
            "Age v MRx Spherical",
             "Age v MRx Cylindrical",
             "Age v MRx Axis",
             "Age v Pachy Min",
             "Age v Pachy Apex",]

k = 0
for h in range(1, TotalnumberOfDataPoints-1,1 ):
    makeplot(h, 0, numberOfCases, titlesAge[k], control, ectasia)
    k += 1

#plotting pachy min v pachy max
makeplot(TotalnumberOfDataPoints-3, TotalnumberOfDataPoints-2, numberOfCases, 'Pachy Max v Pachy Min', control, ectasia)


#plotting mean strain pretreatment v mean strain sim change
makeplot(2,3, numberOfCases, 'Mean Strain Pretreatment v Mean Strain Sim change', control, ectasia)


anotherTitleArray = ["Age",
                     "Mean Strain OutCome",
                     "Mean Strain Change",
                     "Mean Strain Pretreatment",
                     "Max Strain OutCome",
                     "Max Strain Change",
                     "Max Strain Pretreatment",
                     "MRx Spherical",
                     "MRx Cylindrical",
                     "MRx Axis",
                     "Pachy Min",
                     "Pachy Apex",
                     "KMax",
                     "Spherical Equivalence"]

#plotting mean pretreatment strain for both groups
zeross = np.zeros(numberOfCases)
oness = np.ones(numberOfCases)

for p in range(TotalnumberOfDataPoints):
    makeplot1(0,p,numberOfCases, anotherTitleArray[p], control, ectasia, zeross, oness)


#*******************************************************************************
#Going to perform a correlation analysis to verify relationships for probability
#distributions and analytical derivation
#this correlation was only calculated for patients with ectasia
#easily extended to include control patients if needed

newertitles = ["Age & Age",
               "Age & Mean Strain Outcome",
               "Age & Mean Strain Change",
               "Age & Mean Strain Pre",
               "Age & Max Outcome",
               "Age & Max Change",
               "Age & Max Pre",
               "Age & MRx Sph",
               "Age & MRx Cyl",
               "Age & MRx Axis",
               "Age & Pachy Min",
               "Age & Pachy Apex",
               "Age & kmax",
               "Age & Sph Equ",
               "Mean Strain Outcome & Age",
               "Mean Strain Outcome & Mean Strain Outcome",
               "Mean Strain Outcome & Mean Strain Change",
               "Mean Strain Outcome & Mean Strain Pre",
               "Mean Strain Outcome & Max Outcome",
               "Mean Strain Outcome & Max Change",
               "Mean Strain Outcome & Max Pre",
               "Mean Strain Outcome & MRx Sph",
               "Mean Strain Outcome & MRx Cyl",
               "Mean Strain Outcome & MRx Axis",
               "Mean Strain Outcome & Pachy Min",
               "Mean Strain Outcome & Pachy Apex",
               "Mean Strain Outcome & kmax",
               "Mean Strain Outcome & Sph Equ",
               "Mean Strain Change & Age",
               "Mean Strain Change & Mean Strain Outcome",
               "Mean Strain Change & Mean Strain Change",
               "Mean Strain Change & Mean Strain Pre",
               "Mean Strain Change & Max Outcome",
               "Mean Strain Change & Max Change",
               "Mean Strain Change & Max Pre",
               "Mean Strain Change & MRx Sph",
               "Mean Strain Change & MRx Cyl",
               "Mean Strain Change & MRx Axis",
               "Mean Strain Change & Pachy Min",
               "Mean Strain Change & Pachy Apex",
               "Mean Strain Change & kmax",
               "Mean Strain Change & Sph Equ",
               "Mean Strain Pre & Age",
               "Mean Strain Pre & Mean Strain Outcome",
               "Mean Strain Pre & Mean Strain Change",
               "Mean Strain Pre & Mean Strain Pre",
               "Mean Strain Pre & Max Outcome",
               "Mean Strain Pre & Max Change",
               "Mean Strain Pre & Max Pre",
               "Mean Strain Pre & MRx Sph",
               "Mean Strain Pre & MRx Cyl",
               "Mean Strain Pre & MRx Axis",
               "Mean Strain Pre & Pachy Min",
               "Mean Strain Pre & Pachy Apex",
               "Mean Strain Pre & kmax",
               "Mean Strain Pre & Sph Equ",
               "Max Strain Outcome & Age",
               "Max Strain Outcome & Mean Strain Outcome",
               "Max Strain Outcome & Mean Strain Change",
               "Max Strain Outcome & Mean Strain Pre",
               "Max Strain Outcome & Max Outcome",
               "Max Strain Outcome & Max Change",
               "Max Strain Outcome & Max Pre",
               "Max Strain Outcome & MRx Sph",
               "Max Strain Outcome & MRx Cyl",
               "Max Strain Outcome & MRx Axis",
               "Max Strain Outcome & Pachy Min",
               "Max Strain Outcome & Pachy Apex",
               "Max Strain Outcome & kmax",
               "Max Strain Outcome & Sph Equ",
               "Max Strain Change & Age",
               "Max Strain Change & Mean Strain Outcome",
               "Max Strain Change & Mean Strain Change",
               "Max Strain Change & Mean Strain Pre",
               "Max Strain Change & Max Outcome",
               "Max Strain Change & Max Change",
               "Max Strain Change & Max Pre",
               "Max Strain Change & MRx Sph",
               "Max Strain Change & MRx Cyl",
               "Max Strain Change & MRx Axis",
               "Max Strain Change & Pachy Min",
               "Max Strain Change & Pachy Apex",
               "Max Strain Change & kmax",
               "Max Strain Change & Sph Equ",
               "Max Strain Pre & Age",
               "Max Strain Pre & Mean Strain Outcome",
               "Max Strain Pre & Mean Strain Change",
               "Max Strain Pre & Mean Strain Pre",
               "Max Strain Pre & Max Outcome",
               "Max Strain Pre & Max Change",
               "Max Strain Pre & Max Pre",
               "Max Strain Pre & MRx Sph",
               "Max Strain Pre & MRx Cyl",
               "Max Strain Pre & MRx Axis",
               "Max Strain Pre & Pachy Min",
               "Max Strain Pre & Pachy Apex",
               "Max Strain Pre & kmax",
               "Max Strain Pre & Sph Equ",
               "mrx sph & Age",
               "mrx sph & Mean Strain Outcome",
               "mrx sph & Mean Strain Change",
               "mrx sph & Mean Strain Pre",
               "mrx sph & Max Outcome",
               "mrx sph & Max Change",
               "mrx sph & Max Pre",
               "mrx sph & MRx Sph",
               "mrx sph & MRx Cyl",
               "mrx sph & MRx Axis",
               "mrx sph & Pachy Min",
               "mrx sph & Pachy Apex",
               "mrx sph & kmax",
               "mrx sph & Sph Equ",
               "mrx cyl & Age",
               "mrx cyl & Mean Strain Outcome",
               "mrx cyl & Mean Strain Change",
               "mrx cyl & Mean Strain Pre",
               "mrx cyl & Max Outcome",
               "mrx cyl & Max Change",
               "mrx cyl & Max Pre",
               "mrx cyl & MRx Sph",
               "mrx cyl & MRx Cyl",
               "mrx cyl & MRx Axis",
               "mrx cyl & Pachy Min",
               "mrx cyl & Pachy Apex",
               "mrx cyl & kmax",
               "mrx cyl & Sph Equ",
               "mrx axis & Age",
               "mrx axis & Mean Strain Outcome",
               "mrx axis & Mean Strain Change",
               "mrx axis & Mean Strain Pre",
               "mrx axis & Max Outcome",
               "mrx axis & Max Change",
               "mrx axis & Max Pre",
               "mrx axis & MRx Sph",
               "mrx axis & MRx Cyl",
               "mrx axis & MRx Axis",
               "mrx axis & Pachy Min",
               "mrx axis & Pachy Apex",
               "mrx axis & kmax",
               "mrx axis & Sph Equ",
               "pmin & Age",
               "mrx pmin & Mean Strain Outcome",
               "mrx pmin & Mean Strain Change",
               "mrx pmin & Mean Strain Pre",
               "mrx pmin & Max Outcome",
               "mrx pmin & Max Change",
               "mrx pmin & Max Pre",
               "mrx pmin & MRx Sph",
               "mrx pmin & MRx Cyl",
               "mrx pmin & MRx Axis",
               "mrx pmin & Pachy Min",
               "mrx pmin & Pachy Apex",
               "mrx pmin & kmax",
               "mrx pmin & Sph Equ",
               "pmax & Age",
               "mrx pmax & Mean Strain Outcome",
               "mrx pmax & Mean Strain Change",
               "mrx pmax & Mean Strain Pre",
               "mrx pmax & Max Outcome",
               "mrx pmax & Max Change",
               "mrx pmax & Max Pre",
               "mrx pmax & MRx Sph",
               "mrx pmax & MRx Cyl",
               "mrx pmax & MRx Axis",
               "mrx pmax & Pachy Min",
               "mrx pmax & Pachy Apex",
               "mrx pmax & kmax",
               "mrx pmax & Sph Equ",
               "KMax & Age",
               "KMax & Mean Strain Outcome",
               "KMax & Mean Strain Change",
               "KMax & Mean Strain Pre",
               "KMax & Max Outcome",
               "KMax & Max Change",
               "KMax & Max Pre",
               "KMax & MRx Sph",
               "KMax & MRx Cyl",
               "KMax & MRx Axis",
               "KMax & Pachy Min",
               "KMax & Pachy Apex",
               "KMax & Kmax",
               "KMax & Sph Equ",
               "mrx spheq & Age",
               "mrx spheq & Mean Strain Outcome",
               "mrx spheq & Mean Strain Change",
               "mrx spheq & Mean Strain Pre",
               "mrx spheq & Max Outcome",
               "mrx spheq & Max Change",
               "mrx spheq & Max Pre",
               "mrx spheq & MRx Sph",
               "mrx spheq & MRx Cyl",
               "mrx spheq & MRx Axis",
               "mrx spheq & Pachy Min",
               "mrx spheq & Pachy Apex",
               "mrx spheq & kmax",
               "mrx spheq & Sph Equ"]

x=0
for y in range(TotalnumberOfDataPoints):
    for z in range(TotalnumberOfDataPoints):
        #print(newertitles[x])
        ryz = Correlate(ectasia[:,y], ectasia[:,z])
        print(ryz)
        x+=1
        if z == 16:
            print("here")
    print("***************",y,"******************\n")
               



#***************************************************************************************************
#Section for Bayesian Analysis
#first need to figure out what type of distribution each continuous data set

continuous_hist = []
count = []
check = 0
plot_titles = ["Histogram of Mean Strain Sim Outcome",
               "Histogram of Mean Strain Sim Change",
               "Histogram of Mean Strain Pretreatment",
               "Histogram of Max Strain Sim Outcome",
               "Histogram of Max Strain Sim Change",
               "Histogram of Max Strain Pretreatment",
               "Histogram of MRx Spherical",
               "Histogram of MRx Cylindrical",
               "Histogram of MRx Axis",
               "Histogram of Pachy Min",
               "Histogram of Pachy Apex",
               "Histogram of Spherical Equivalence"]

for u in range(TotalnumberOfDataPoints):
    continuous_hist.clear()
    count.clear()
    continuous_hist.append(ectasia[0,u])
    count.append(1)
    for y in range(numberOfCases-1):
        check = 0
        for h in range(len(continuous_hist)):
            if continuous_hist[h] == ectasia[y+1,u]:
                count[h] += 1
                check = 1
        if check == 0:
            continuous_hist.append(ectasia[y+1,u])
            count.append(1)
    plt.title(plot_titles[u])
    plt.plot(continuous_hist,count, 'b^')
    plt.show()



#let's calculate the variance for all of the data points
print("AVERAGES")
variance = []
for o in range(TotalnumberOfDataPoints):
    variance.append(var(numberOfCases, ectasia[:,o]))

print("\n")
print("VARIANCES")
print(variance)

#now we want to bin the more continuous data
#*******************************
#Data to NOT be binned:
#MRx Spherical and Cylindrical
#Columns 6 and 7 in Ectasia table
#*******************************


binvariance = []
efficiencyfactor = 0
k = 15 #number of bins for data that is not already quantized
binloc = np.zeros((k, TotalnumberOfDataPoints),float) #bin locations on x axis
counts = np.zeros((k, TotalnumberOfDataPoints),float) # histogram count
bintab = np.zeros((numberOfCases, TotalnumberOfDataPoints),float) #renaming ectasia table but using binned entries as substitutes

for m in range(TotalnumberOfDataPoints):    
    #find max and min of data
    for w in range(numberOfCases):
        if w == 0:
            maxi = ectasia[w,m]
            mini = ectasia[w,m]
        if w > 0:
            if ectasia[w,m] > maxi:
                maxi = ectasia[w,m]
            if ectasia[w,m] < mini:
                mini = ectasia[w,m]

    #set up a k-split binning process
    titlesagain = ["Binned Historgram Mean SSO",
                   "Binned Historgram Mean SSC",
                   "Binned Historgram Mean SP",
                   "Binned Historgram Max SSO",
                   "Binned Historgram Max SSC",
                   "Binned Historgram Max SP",
                   "Binned Historgram MRx Spherical",
                   "Binned Historgram MRx Cylindrical",
                   "Binned Historgram MRx Axis",
                   "Binned Historgram Pachy Min",
                   "Binned Historgram Pachy Apex",
                   "Binned Historgram Spherical Equivalence"]
                       
    if m != 6 and m != 7:  #already have the data I need for this in the ectasia table because it is already quantized so these rows of the tables will just be blank
        datrange = maxi - mini
        binsize = datrange/k #set bin size
        if(m == 1):
            print(datrange, binsize, k)
            print("HERE^")
        loc = mini + binsize/2 #set first bin mean
        for r in range(k): #set up bin means
            if r > 0:
                loc += binsize
            binloc[r,m] = loc
                
        for d in range(numberOfCases): #bin the data
            for y in range(k):
                if abs(ectasia[d,m]-binloc[y,m]) <= binsize/1.9999999999999:
                    counts[y,m]+=1
                    bintab[d,m] = binloc[y,m]
        plt.title(titlesagain[m])
        plt.plot(binloc[:,m],counts[:,m], 'b^')
        #plt.show()
        a = binvar(k, numberOfCases, binloc[:,m], counts[:,m], ectasia[:,m])
        print(a/variance[m], sum(counts[:,m]))


#Now want to create a three dimensional histogram of the necessary data
#Start with comparing MSC and MRx
#use bintab and binloc for MSC

#need a binloc array for MRx Sph
u = 0
mrxspher = []
while u >= -10:
    mrxspher.append(u)
    u -= .25

#******************************************************************************
#Fourth iteration
#Includes Variables: MSC,MaxSC, MRxS,MSP,MaxSP, PM, PA, MRxC, Age, and KMax
#Binning everything but MRx variables because everything else is continuous

#let's calculate the variance for all of the data points
print("AVERAGES")
variance = []
for o in range(TotalnumberOfDataPoints):
    variance.append(math.sqrt(var(numberOfCases, ectasia[:,o])))

print("\n")
print("VARIANCES")
print(variance)

#now we want to bin the more continuous data
#*******************************
#Data to NOT be binned:
#MRx Spherical and Cylindrical
#Columns 6 and 7 in Ectasia table
#*******************************


binvariance = []
efficiencyfactor = 0
keratoconuscount = 0
k = 15 #number of bins for data that is not already quantized
binloc = np.zeros((k, TotalnumberOfDataPoints),float) #bin locations on x axis
counts = np.zeros((k, TotalnumberOfDataPoints),float) # histogram count
bintab = np.zeros((numberOfCases, TotalnumberOfDataPoints),float) #renaming ectasia table but using binned entries as substitutes

for m in range(TotalnumberOfDataPoints):    
    #find max and min of data
    for w in range(numberOfCases):
        if (m == 12 and ectasia[w,m] > 50):
            keratoconuscount += 1
        if w == 0:
            maxi = ectasia[w,m]
            mini = ectasia[w,m]
        if w > 0:
            if ectasia[w,m] > maxi:
                if (m == 12 and ectasia[w,m] < 200):
                    maxi = ectasia[w,m]
                if m != 12:
                    maxi = ectasia[w,m]
            if ectasia[w,m] < mini:
                mini = ectasia[w,m]
    print(mini,maxi, keratoconuscount)

    #set up a k-split binning process
    titlesagain = ["Binned Historgram Mean SSO",
                   "Binned Historgram Mean SSC",
                   "Binned Historgram Mean SP",
                   "Binned Historgram Max SSO",
                   "Binned Historgram Max SSC",
                   "Binned Historgram Max SP",
                   "Binned Historgram MRx Spherical",
                   "Binned Historgram MRx Cylindrical",
                   "Binned Historgram MRx Axis",
                   "Binned Historgram Pachy Min",
                   "Binned Historgram Pachy Apex",
                   "Binned Historgram Spherical Equivalence"]
                       
    if m != 7 and m != 8:  #already have the data I need for this in the ectasia table because it is already quantized so these rows of the tables will just be blank
        datrange = maxi - mini
        binsize = datrange/k #set bin size
        #if(m == 1):
            #print(datrange, binsize, k)
            #print("HERE^")
        loc = mini + binsize/2 #set first bin mean
        for r in range(k): #set up bin means
            if r > 0:
                loc += binsize
            binloc[r,m] = loc
                
        for d in range(numberOfCases): #bin the data
            for y in range(k):
                if abs(ectasia[d,m]-binloc[y,m]) <= binsize/1.9999999999999:
                    counts[y,m]+=1
                    bintab[d,m] = binloc[y,m]
        #plt.title(titlesagain[m])
        #plt.plot(binloc[:,m],counts[:,m], 'b^')
        #plt.show()
        a = binvar(k, numberOfCases, binloc[:,m], counts[:,m], ectasia[:,m])
        #print(a/variance[m], sum(counts[:,m]))


#Now want to create a three dimensional histogram of the necessary data
#Start with comparing MSC and MRx
#use bintab and binloc for MSC

#need a binloc array for MRx Sph and MRx Cyl
u = 0
mrxspher = []
while u >= -10:
    mrxspher.append(u)
    u -= .25

#want to construct the five probability distributions
#for MRx Spherical
sphtable = np.zeros((len(mrxspher), 2),float)
for v in range(len(mrxspher)):
    sphtable[v,0] = mrxspher[v]
    for io in range(len(ectasia[:,7])):
        if ectasia[io,7] == mrxspher[v]:
            sphtable[v,1] += 1

w = 0
mrxcyl = []
while w <= 5:
    mrxcyl.append(w)
    w += .25

#want to construct the five probability distributions
#for MRx Cylindrical
cyltable = np.zeros((len(mrxcyl), 2),float)
for v in range(len(mrxcyl)):
    cyltable[v,0] = mrxcyl[v]
    for io in range(len(ectasia[:,8])):
        if ectasia[io,8] == mrxcyl[v]:
            cyltable[v,1] += 1


#*********************************************************************************
#binning control data prepping for ROC analysis

#let's calculate the variance for all of the data points
print("CONTROL AVERAGES")
varianceC = []
for o in range(TotalnumberOfDataPoints):
    varianceC.append(math.sqrt(var(numControl, control[:,o])))

print("\n")
print("CONTROL VARIANCES")
print(varianceC)

#now we want to bin the more continuous data
#*******************************
#Data to NOT be binned:
#MRx Spherical and Cylindrical
#Columns 6 and 7 in Ectasia table
#*******************************


binvarianceC = []
efficiencyfactor = 0
keratoconuscountC = 0
k = 15 #number of bins for data that is not already quantized
binlocC = np.zeros((k, TotalnumberOfDataPoints),float) #bin locations on x axis
countsC = np.zeros((k, TotalnumberOfDataPoints),float) # histogram count
bintabC = np.zeros((numControl, TotalnumberOfDataPoints),float) #renaming ectasia table but using binned entries as substitutes

for m in range(TotalnumberOfDataPoints):    
    #find max and min of data
    for w in range(numControl):
        if (m == 12 and control[w,m] > 50):
            keratoconuscountC += 1
        if w == 0:
            maxi = control[w,m]
            mini = control[w,m]
        if w > 0:
            if control[w,m] > maxi:
                maxi = control[w,m]
            if control[w,m] < mini:
                mini = control[w,m]
        #if m == TotalnumberOfDataPoints-1:
            #if control[w,m] >= 0:
                #print("here")
    print(mini,maxi, keratoconuscountC)

    #set up a k-split binning process
    titlesagain = ["Binned Historgram Mean SSO",
                   "Binned Historgram Mean SSC",
                   "Binned Historgram Mean SP",
                   "Binned Historgram Max SSO",
                   "Binned Historgram Max SSC",
                   "Binned Historgram Max SP",
                   "Binned Historgram MRx Spherical",
                   "Binned Historgram MRx Cylindrical",
                   "Binned Historgram MRx Axis",
                   "Binned Historgram Pachy Min",
                   "Binned Historgram Pachy Apex",
                   "Binned Historgram Spherical Equivalence"]
                       
    if m != 7 and m != 8:  #already have the data I need for this in the ectasia table because it is already quantized so these rows of the tables will just be blank
        datrange = maxi - mini
        binsize = datrange/k #set bin size
        #if(m == 1):
            #print(datrange, binsize, k)
            #print("HERE^")
        loc = mini + binsize/2 #set first bin mean
        for r in range(k): #set up bin means
            if r > 0:
                loc += binsize
            binlocC[r,m] = loc
                
        for d in range(numControl): #bin the data
            for y in range(k):
                if abs(control[d,m]-binlocC[y,m]) <= binsize/1.9999999999999:
                    countsC[y,m]+=1
                    bintabC[d,m] = binlocC[y,m]
        #plt.title(titlesagain[m])
        #plt.plot(binloc[:,m],counts[:,m], 'b^')
        #plt.show()
        a = binvar(k, numControl, binlocC[:,m], countsC[:,m], control[:,m])
        #print(a/varianceC[m], sum(countsC[:,m]))


#Now want to create a three dimensional histogram of the necessary data
#Start with comparing MSC and MRx
#use bintab and binloc for MSC

#need a binloc array for MRx Sph and MRx Cyl
u = 0
mrxspherC = []
while u >= -10:
    mrxspherC.append(u)
    u -= .25

#want to construct the five probability distributions
#for MRx Spherical
sphtableC = np.zeros((len(mrxspherC), 2),float)
for v in range(len(mrxspherC)):
    sphtableC[v,0] = mrxspherC[v]
    for io in range(len(control[:,7])):
        if control[io,7] == mrxspherC[v]:
            sphtableC[v,1] += 1

w = 0
mrxcylC = []
while w <= 5:
    mrxcylC.append(w)
    w += .25

#want to construct the five probability distributions
#for MRx Cylindrical
cyltableC = np.zeros((len(mrxcylC), 2),float)
for v in range(len(mrxcylC)):
    cyltableC[v,0] = mrxcylC[v]
    for io in range(len(control[:,8])):
        if control[io,8] == mrxcylC[v]:
            cyltableC[v,1] += 1


#printing data for all roc curves to be read by Mathematica
output = open("0e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,0], counts[h,0]))

output.close()

output = open('0c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,0], countsC[h,0]))

output.close()

output = open("1e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,1], counts[h,1]))

output.close()

output = open('1c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,1], countsC[h,1]))

output.close()

output = open("2e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,2], counts[h,2]))

output.close()

output = open('2c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,2], countsC[h,2]))

output.close()

output = open("3e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,3], counts[h,3]))

output.close()

output = open('3c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,3], countsC[h,3]))

output.close()

output = open("4e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,4], counts[h,4]))

output.close()

output = open('4c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,4], countsC[h,4]))

output.close()

output = open("5e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,5], counts[h,5]))

output.close()

output = open('5c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,5], countsC[h,5]))

output.close()

output = open("6e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,6], counts[h,6]))

output.close()

output = open('6c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,6], countsC[h,6]))

output.close()

output = open("7e.txt", 'w+')

for h in range(len(sphtable[:,0])):
    output.write("%f %f\n" % (sphtable[h,0], sphtable[h,1]))

output.close()

output = open('7c.txt', 'w+')

for h in range(len(sphtableC[:,0])):
    output.write("%f %f\n" % (sphtableC[h,0], sphtableC[h,1]))

output.close()

output = open("8e.txt", 'w+')

for h in range(len(cyltable[:,0])):
    output.write("%f %f\n" % (cyltable[h,0], cyltable[h,1]))

output.close()

output = open('8c.txt', 'w+')

for h in range(len(cyltableC[:,0])):
    output.write("%f %f\n" % (cyltableC[h,0], cyltableC[h,1]))

output.close()

output = open("10e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,10], counts[h,10]))

output.close()

output = open('10c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,10], countsC[h,10]))

output.close()

output = open("11e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,11], counts[h,11]))

output.close()

output = open('11c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,11], countsC[h,11]))

output.close()

output = open("12e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,12], counts[h,12]))

output.close()

output = open('12c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,12], countsC[h,12]))

output.close()

output = open("13e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,13], counts[h,13]))

output.close()

output = open('13c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,13], countsC[h,13]))

output.close()

output = open("14e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,14], counts[h,14]))

output.close()

output = open('14c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,14], countsC[h,14]))

output.close()

output = open("15e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,15], counts[h,15]))

output.close()

output = open('15c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,15], countsC[h,15]))

output.close()

output = open("16e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,16], counts[h,16]))

output.close()

output = open('16c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,16], countsC[h,16]))

output.close()

output = open("17e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,17], counts[h,17]))

output.close()

output = open('17c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,17], countsC[h,17]))

output.close()

output = open("18e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,18], counts[h,18]))

output.close()

output = open('18c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,18], countsC[h,18]))

output.close()

output = open("badde.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,19], counts[h,19]))

output.close()

output = open('baddc.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,19], countsC[h,19]))

output.close()

output = open("20e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,20], counts[h,20]))

output.close()

output = open('20c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,20], countsC[h,20]))

output.close()

output = open("21e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,21], counts[h,21]))

output.close()

output = open('21c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,21], countsC[h,21]))

output.close()

output = open("22e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,22], counts[h,22]))

output.close()

output = open('22c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,22], countsC[h,22]))

output.close()

output = open("23e.txt", 'w+')

for h in range(len(binloc[:,0])):
    output.write("%f %f\n" % (binloc[h,23], counts[h,23]))

output.close()

output = open('23c.txt', 'w+')

for h in range(len(binlocC[:,0])):
    output.write("%f %f\n" % (binlocC[h,23], countsC[h,23]))

output.close()

























