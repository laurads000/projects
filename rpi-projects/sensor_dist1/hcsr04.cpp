#include <iostream>
#include <pigpio.h>

#include "hcsr04.h"

HCSR04::HCSR04(int t, int e): mOutputGPIO(-1), mInputGPIO(-1) {
    initialize(t, e);
}

HCSR04::~HCSR04(){
    if (mPiGpioInit >= 0) {
        gpioTerminate();
    }
}

uint32_t HCSR04::getEchoTimeout(){
    return echoTimeout;
}

double HCSR04::getTrigHighTime(){
    return trigHighTime;
}

double HCSR04::getDistance() {
    uint32_t startTick = 0;
    uint32_t elapsedTick = 0;
    double distance = 0.0;
    
    //time_sleep(0.001);
    gpioWrite(mOutputGPIO, PI_LOW);
    time_sleep(0.000005);
    gpioWrite(mOutputGPIO, PI_HIGH);
    time_sleep(getTrigHighTime()); // 10 us
    gpioWrite(mOutputGPIO, PI_LOW);

    // wait until echo pin goes high
    while(gpioRead(mInputGPIO) == PI_LOW) {
        // do nothing
    }

    // assume mInputGPIO is HIGH
    startTick = gpioTick();
    while((elapsedTick = gpioTick()-startTick) < getEchoTimeout()) {  // timeout is 38 ms.
        if(gpioRead(mInputGPIO) == PI_LOW){
		    break;
	    }
	//    std::cout << "elapsedTick = " << elapsedTick << "\n";
    }

    // std::cout << "Final elapsedTick = " << elapsedTick << "\n";

    if(elapsedTick < getEchoTimeout()) {
        distance = (0.034*elapsedTick)/2.0;
    } else {
	    std::cout << "sensor timed out\n";
    } 

    std:: cout << distance << "\n";
    return distance;
}

void HCSR04::initialize(int trigger, int echo) {
    mOutputGPIO = trigger;
    mInputGPIO = echo;
    if(gpioInitialise() >= 0){
        mPiGpioInit = 1;
        gpioSetMode(mOutputGPIO, PI_OUTPUT); //Write mode
        gpioSetMode(mInputGPIO, PI_INPUT);   // Read mode
        gpioWrite(mOutputGPIO, PI_LOW);
        time_sleep(0.5);  // sleep for 500ms.
    } else {
        std::cout << "gpioInitialise() failed\n";
    }
}

