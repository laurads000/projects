#ifndef _HCSR04_H_
#define _HCSR04_H_


class HCSR04 
{
    public:
      HCSR04(int t, int e);
      ~HCSR04();
      double getDistance();
	  uint32_t getEchoTimeout();
	  double getTrigHighTime();
        
    private:
        void initialize(int trigger, int echo);
        int mOutputGPIO = -1;
        int mInputGPIO = -1;
        int mPiGpioInit = -1;
	    const uint32_t echoTimeout = 38000; // timeout for echo signal is 38000 us
	    const double trigHighTime = 0.00001; // set trigger pin HIGH for 0.00001s 
};



#endif // _HCSR04_H_
