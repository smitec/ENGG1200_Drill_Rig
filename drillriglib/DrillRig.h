#ifndef __PROJECT__D__H__
#define __PROJECT__D__H__

#include "Arduino.h"

#define RED 800
#define BLUE 600

typedef unsigned int uint;

class DrillRig {
	public:
		DrillRig();
		void initialise(uint baud);
		void send_feed_rate(uint rate);
		void send_calculated_depth_mm(uint depth);
		void send_calculated_torque(double torque);
		void send_material_density(double density);
        void send_stop_command();
		uint get_analog_from_simulink();
	private:
		int _feed;
		int _mode;
		
		uint read_uint();
		void send_uint(uint data);
		unsigned char wait_and_read();
};

#endif
