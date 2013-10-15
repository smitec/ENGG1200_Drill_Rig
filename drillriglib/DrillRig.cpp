#include "DrillRig.h"

/* TODO:
	- end message
	- density types
*/


DrillRig::DrillRig() {
	this->_feed = 0;
	this->_mode = -1;
}
void DrillRig::initialise(uint baud) {
	uint mode, value;
	pinMode(13, OUTPUT);
	
	Serial.begin(baud);
	
	Serial.write('s')
	wait_and_read();
	this->_mode = 0

}

void DrillRig::send_feed_rate(uint ratei, bool up) {
    if (this->_mode == 0) {
		this->send_uint(1);
		this->send_uint(rate);
    }
}

void DrillRig::send_calculated_depth_mm(uint depth) {
	this->send_uint(2);
	this->send_uint(depth);
}

void DrillRig::send_calculated_torque(double torque) {
	uint t = (uint)(torque*1000);
	this->send_uint(3);
	this->send_uint(t);
}

void DrillRig::send_material_density(double density) {
	this->send_uint(4);
	this->send_uint((uint)density);
}

uint DrillRig::get_analog_from_simulink() {
	return this->read_uint();
}

uint DrillRig::read_uint() {
	unsigned char low, high;
	low = this->wait_and_read();
	high = this->wait_and_read();
	
	return (uint)((high << 8) | (low));
}

void DrillRig::send_uint(uint data) {
	Serial.write((uint)(data & 0xFF));
	Serial.write((uint)((data >> 8) & 0xFF));
}

unsigned char DrillRig::wait_and_read() {
	while(!Serial.available());
	return Serial.read();
}
