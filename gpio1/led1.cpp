#include <iostream>
#include <chrono>
#include <thread>
#include <pigpio.h>

int main( int argc, char** argv)
{
	if(gpioInitialise() < 0){
		std::cout << "Error initializing gpio library\n";
	}else{
		// gpio library initialized. 
		gpioSetMode(4, PI_OUTPUT);
		for( int i=0; i < 10; i++){
			gpioWrite(4, PI_HIGH);  
			std::this_thread::sleep_for(std::chrono::seconds(1));
			gpioWrite(4, PI_LOW);
			std::this_thread::sleep_for(std::chrono::seconds(1));
		} //endif
		gpioTerminate();
	}//endif
} //end main 
