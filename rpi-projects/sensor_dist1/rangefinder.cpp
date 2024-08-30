#include <iostream>
#include <pigpio.h>
#include <functional>

#include "rangefinder.h"


RangeFinder::RangeFinder():myHCSR04(nullptr) {
    myHCSR04 = new HCSR04(4, 23);
} 

RangeFinder::~RangeFinder() {
    delete myHCSR04;
}

bool RangeFinder::isObjectInRange(int minDist, int maxDist, uint32_t duration, const std::function<void(double)> &f){
    if(minDist > maxDist) {
        return false;
    } else {
        uint32_t startTick = gpioTick();
        uint32_t endTick = 0;
        double distance = 0.0;
        do {
            distance = myHCSR04->getDistance();
            if ((minDist < distance) && (distance < maxDist)){
                f(distance);
            }
            endTick = gpioTick();
            std::cout << "elapsed time = " << (endTick-startTick)/1000000 << "\n";
        } while((endTick - startTick) <= duration);
    }
    return true;
}

