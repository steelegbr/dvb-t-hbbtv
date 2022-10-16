# HackRF DVB-T Notes

The included dvb_tx_8k.grc file is slightly adapted from the GNU Radio examples. To work with the HackRF One, the osmocom addons must be installed. To do this on Ubuntu:

    sudo apt install gr-osmosdr

The osmocom Sink must also have the following parameters:

* Device Arguments: hackrf=0
* Sync: PC Clock
* Sample Rate (sps): samp_rate
* Frequency: center_freq
* RF Gain: 14dB (Max)
* IF Gain: 40dB (Max)
* BB Gain: 62dB (Max)
* Bandwidth: 8.75MHz

# Underruns

If your processor is not fast enough, you will encounter UUUUU and a failure to transmit. This is how I found out a Macbook is not powerful enough for this flow.

# Transport Stream

The example transport stream from the original flow did not work with the TV I transmitted to. This resulted in lost time troubleshooting.

The tsduck examples captured from British TV for a DVB-T multiplex (NOT DVB-T2) worked correctly.