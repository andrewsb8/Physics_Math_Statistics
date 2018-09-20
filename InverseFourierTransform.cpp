/*

This program is designed to calculate the Inverse Fourier Transform of a set 
of data which is read by the program.  Measurements used throughout are 
declared as global variables.  Data input is stored in dynamic arrays so that
size of the data set need not be known.  This program does not normalize the data
mainly because it cannot interpret change in variables and therefore different normalization
factors for different sets of data.
Author: Brian Andrews
Last Date Modified: 2/28/16

*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <fstream.h>
#include <vector.h>
#include <iostream>

//our only function
void DiscreteFourierTransform();

//constants
double TwoPI = 2*M_PI;

//measurement variables for lab, can be changed easily in needed in future.
//arguments for the exponential
double lambda = .5435; //wavelength of green light in microns
double length = 921000; //length from laser to CCD in microns
double dy = 7.4; //pixel size in microns, integration variable

//arrays for storing the data
vector<double> Efieldmag;
vector<double> separation;
vector<double> FTresults;
vector<double> integrationvariable;


int main()
{
    //dummy variable
    double temp;
    //input file objects
    ifstream instream;
    ifstream instream2;
    
    //read the two data files and store them in two separate vectors
    instream.open("Emag.txt");
    
    while(!instream.eof())
    {
        instream >> temp;
        Efieldmag.push_back(temp);
    }
    
    instream2.open("distance.txt");
    
    while(!instream2.eof())
    {
        instream2 >> temp;   
        separation.push_back(temp);
    }   
    
    //calling the function now that we have our data
    DiscreteFourierTransform();   
    
    //setting up an output file
    ofstream outputFT;
    outputFT.open("FTdata.txt");
    
    for(int k = 0; k<FTresults.size(); k++)
    {
         outputFT << integrationvariable[k] << " " << FTresults[k] << "\n";
    }
    
    instream.close();
    instream2.close(); 
    outputFT.close();      
    
    system("PAUSE");
    return 0;
}

void DiscreteFourierTransform()
{
    //another dummy variable
    double temp; 
    
    double N = Efieldmag.size();
    
    //integration variable  
    for(int i = -475; i < 475; i++)
    {
        temp = 0;
        integrationvariable.push_back(i);
            for(int k = 0; k < Efieldmag.size(); k++)
            {
                 temp = temp + (2*Efieldmag[k]*cos((TwoPI/(lambda*length))*separation[k]*i)*dy);
            }
            
        FTresults.push_back(temp);
    }
}      
    
                    
    
  
    
    
    
    
    
    
 
