import numpy as np


def dbm2watt(dbm):
    """
    Performs the conversion of power from dBm to Watt.

    Parameters: dbm - power in dBm
    Results: power in Watts
    """
    return 10 ** (dbm / 10) / 1000


def watt2dbm(watt):
    """
    Performs the conversion of power from Watt to dBm.

    Parameters: watt - power in Watts
    Results: power in dBm
    """
    return 10 * np.log10(1000 * watt)


class Antenna:
    """
    Class responds for the radio channel between user equipment (user) and base station,
    located on UAV (drone). Each method is well commented, but you can find more information
    about it in simulator's documentation.
    Analytic calculation of power received by user equipment is calculated by
    Friis transmission equation. Description and formulas here:
    https://www.pasternack.com/t-calculator-friis.aspx
    """

    def __init__(self, parameters):
        self.transmit_power = parameters['transmit_power']
        self.transmission_bandwidth = parameters['transmission_bandwidth']
        self.carrier_frequency = parameters['carrier_frequency']
        self.receive_antenna_gain = parameters['receive_antenna_gain']
        self.transmit_antenna_gain = parameters['transmit_antenna_gain']
        self.noise_power = -174 + 10 * np.log10(self.transmission_bandwidth)
        self.light_speed = 300_000_000  # m/s

    def friis_equation(self, distance):
        """
        Calculate the power received by user in dBm
        Description and formulas here: https://www.pasternack.com/t-calculator-friis.aspx

        Parameters: distance - distance [meters] in 3D space between user and drone
        Results: Received power in dBm
        """
        log_num = 20 * np.log10(self.light_speed / (4 * np.pi * distance * self.carrier_frequency))
        return self.transmit_power + self.receive_antenna_gain + self.transmit_antenna_gain + log_num

    def calculate_snr(self, distance):
        """
        Calculate SNR between user and nearest drone based on distance between them.

        Parameters: distance - distance [meters]
        Results: SNR in dB
        """
        noise_power_w = dbm2watt(self.noise_power)
        receive_power = self.friis_equation(distance)
        receive_power_w = dbm2watt(receive_power)
        return 10 * np.log10(receive_power_w / noise_power_w)

    def get_distance_on_snr(self, snr_threshold):
        """
        Reversed calculations from 'calculate_snr' method.
        Calculate optimal distance between user and drone based on predefined threshold

        Parameters: snr_threshold - SNR threshold
        Results: distance
        """

        noise_power_w = dbm2watt(self.noise_power)

        received_power_w = noise_power_w * 10 ** (snr_threshold / 10)
        received_power = watt2dbm(received_power_w)

        sum_log = received_power - self.transmit_power - self.receive_antenna_gain - self.transmit_antenna_gain
        return self.light_speed / (4 * np.pi * self.carrier_frequency * 10 ** (sum_log / 20))

    def change_transmit_power(self, new_transmit_power):
        self.transmit_power = new_transmit_power
