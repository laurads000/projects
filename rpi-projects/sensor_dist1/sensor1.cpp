#include <iostream>
#include "rangefinder.h"

class FunctionObject
{
    public:
	void operator()(double d);


};


void FunctionObject::operator()(double d){
    std::cout << "Object found " << d << "cm away.\n";
}


int main() 
{


/*
    double objDistance = 0.0;
    for(int i=0;i<120;i++) {
        if ((objDistance = mySensor.getDistance()) > 0.0) {
            std::cout << "Object detected " << objDistance << "cm away.\n";
        } else {
            std::cout << "No object detected.\n";
        }
        time_sleep(1.0);
    }

*/

    RangeFinder myRangeFinder;
    FunctionObject myFunctionObject;
    if (myRangeFinder.isObjectInRange(0, 500, 100000000, myFunctionObject) == false) {
        std::cout << "Invalid maximum and minimum distances.\n";
    } 

     
    return 0;
} 
