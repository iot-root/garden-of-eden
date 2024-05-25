import board
import adafruit_pct2075
import logging

def get_pcb_temperature():
    i2c = board.I2C()  # uses board.SCL and board.SDA
    pct = adafruit_pct2075.PCT2075(i2c, address=0x48)
    
    return pct.temperature

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    """
    If the module is executed as a standalone script, it will return the pcb_temp in a telegraf friendly format. 
    """
    parser = argparse.ArgumentParser(description='Control an IoT distance sensor.')
    parser.add_argument('--log', action='store_true')
    args = parser.parse_args()

    try:
        pcb_temp = get_pcb_temperature()
        logging.info(f"pbc_temp, value={pcb_temp:.2f}")
    except Exception as e:
        logging.info(f"Error: {e}")
    except KeyboardInterrupt:
        logging.info("Script interrupted.")

    if args.log:
        logging.info(f"PCB Temp, value={pcb_temp:.2f}")