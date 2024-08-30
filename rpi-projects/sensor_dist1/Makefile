PROJECT := sensor1

CXX = g++
CXXFLAGS =  -Wall -pthread 
LDLIBS = -lpigpio -lrt

OBJS := sensor1.o rangefinder.o hcsr04.o
   
$(PROJECT) : $(OBJS)
	$(CXX) $(LDFLAGS) $^ -o $@  $(LDLIBS)


# Additional specific pre-requisites for some .o target files
sensor1.o : rangefinder.h

# Generic pre-requisites for .o target files
%.o: %.cpp %.h
	$(CXX) -c $(CXXFLAGS) $< -o $@
%.o: %.cpp 
	$(CXX) -c $(CXXFLAGS) $< -o $@

clean:
    rm -f *.o
