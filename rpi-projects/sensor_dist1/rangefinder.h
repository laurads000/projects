#ifndef _RANGEFINDER_H_
#define  _RANGEFINDER_H_

#include <functional>

#include "hcsr04.h"

class RangeFinder
{
    public:
        RangeFinder();    
        ~RangeFinder();
        // Determines whether an object lies within the specified range and if so, calls the listener. 
        bool isObjectInRange(int minDist, int maxDist, uint32_t duration, const std::function<void(double)> &f); 

    private:
	   HCSR04* myHCSR04;
};


#endif // _RANGEFINDER_H_
