# EEPROM
This documentation details how the PlanktoScope software’s eeprom program effectively manages the writing, reading, and editing of critical hardware information stored on the EEPROM chip embedded within the PlanktoScope HAT. By encoding essential hardware parameters on this chip, the eeprom program enables the PlanktoScope to store and retrieve system information consistently, ensuring accurate configuration, efficient tracking, and enhanced reproducibility across different hardware setups. This stored data empowers users to seamlessly identify and verify device-specific details, supporting a robust and streamlined approach to hardware management within the PlanktoScope ecosystem.

## Stored Information
Below is the information that is stored on the EEPROM chip:
- `eeprom_planktoscope_ref` : PlanktoScope reference
- `acq_planktoscope_sn` : PlanktoScope serial number
- `acq_planktoscope_version` : PlanktoScope version
- `acq_planktoscope_date_factory` : PlanktoScope fabrication date
- `acq_hat_sn` : HAT serial number
- `acq_hat_version` : HAT version
- `eeprom_driver_ref` : Driver reference
- `eeprom_pump_driver` : Pump reference
- `eeprom_focus_ref` : Stepper focus reference
- `eeprom_obj_lens_ref` : Objective lens reference
- `eeprom_tube_lens_ref` : Tube lens reference
- `eeprom_flowcell_thickness` : Flowcell thickness
- `eeprom_led_ref` : LED reference

The fields stored on the EEPROM, are positioned at fixed starting addresses with specific byte lengths. This structured allocation allows each field to be stored efficiently while maintaining separation from neighboring data entries, facilitating both accurate retrieval and precise editing.

| Field                          | Start address   | Reserved size (in byte) |
|--------------------------------|:---------------:|:-----------------------:|
| eeprom_planktoscope_ref        | 0x0000          | 12                      |
| acq_planktoscope_sn            | 0x000           | 6                       |
| acq_planktoscope_version       | 0x0012          | 6                       |
| acq_planktoscope_date_factory  | 0x0018          | 10                      |
| acq_hat_sn                     | 0x0022          | 13                      |
| acq_hat_version                | 0x002F          | 6                       |
| eeprom_driver_ref              | 0x0035          | 12                      |
| eeprom_pump_ref                | 0x0041          | 12                      |
| eeprom__focus_ref              | 0x004D          | 12                      |
| eeprom_obj_lens_ref            | 0x0059          | 12                      |
| eeprom_tube_lens_ref           | 0x0065          | 12                      |
| eeprom_flowcell_thickness      | 0x0071          | 12                      |
| eeprom_led_ref                 | 0x007D          | 12                      |

## Write eeprom operation
The *write operation* on the EEPROM allows data from Node-RED, presented in key-value format, to be stored in the correct locations. The fabrication date is converted from the format 'YYYY/MM/DD' to 'YYYYMMDD' to optimize storage. 
Initially, the incoming data undergoes verification to confirm that each required field is present. Once verified, each field’s value is converted to ASCII bytes for compatibility with the EEPROM’s storage format. 
Writing to the EEPROM is performed using the `write_i2c_block_data` method included into the *smbus* library (https://pypi.org/project/smbus-cffi/). This method enables writing blocks of data to the EEPROM chip by specifying the EEPROM's address (default is 0x50) and a starting address, which represents the memory location where the first byte will be written.

The EEPROM’s addressing system uses a 16-bit scheme, which is split into two 8-bit parts—high and low bytes—for precise address handling. The address calculation ensures data is stored in the correct memory locations, using the command:

```python
mem_addr_high = (current_addr>>8) & 0xFF
mem_addr_low = current_addr & 0xFF
```
from the `_get_memory_address_bytes` method, with 'current_addr' representing the address of the EEPROM's memory where we want to store the data (formatted like 0x0000).

The EEPROM currently used in the PlanktoSCope HAT is organized into 32-byte pages, requiring each *write operation* to respect page boundaries to avoid unexpected data overlaps, known as “data wrapping.”. This page limit is represented by the `MAX_BLOCK_SIZE` variable.
In the `_write_on_eeprom` method, the `page_boundary` variable calculates how many bytes can be written on the current page before hitting its end. This is calculated by:

```Python
MAX_BLOCK_SIZE - (current_addr % MAX_BLOCK_SIZE)
```
 This ensures that each *write operation* stops at the page boundary. Thus securing efficient and reliable data storage.

Although not currently in use, the software includes functionality to manage the EEPROM's write control. This is achieved by interacting with the write protect pin (WP) of the EEPROM via the connected GPIO pin using `OutputDecvice` from the *gpiozero* library (https://gpiozero.readthedocs.io/en/latest/). By default, the write protection is enabled.

```Python
self._write_control = OutputDevice(gpio_pin, active_high=True)
```

Before each *write operation* the write control is disabled and then re-enabled afterward to prevent any accidental writes to the chip

## Read eeprom operation
The read operation retrieves data from the EEPROM and sends it to Node-RED for display. This is accomplished using the `read_byte` method from the *smbus* library (https://pypi.org/project/smbus-cffi/), which facilitates the extraction of EEPROM data.

To utilize this method, an internal address pointer must be set. This pointer specifies the read position within the EEPROM, ensuring that data is accessed from the correct memory location. Failing to set it could result in reading from an unintended location. 
The pointer configuration is done using the `write_byte_data` function from the *smbus2* library:

```Python
self._bus.write_byte_data(self._eeprom_address, mem_addr_high, mem_addr_low)
``` 
Once the pointer is set, a specified number of bytes, representing the information reserved size of each piece of information, is read starting from the designed memory location. After all bytes of an information have been retrieved, each byte is converted into its ASCII character. Any empty bytes, resulting from information shorter than its reserved space, are removed. The resulting characters are then combined to form a readable string.

```Python
result = ''.join([chr(byte) for byte in data if byte != 0x00])
all_data.append(result)
```

This process is repeated for each piece of information stored on the EEPROM chip. In the end, all retrieved information are stored in a list and linked to their corresponding label.

The read process hence results in a complete dataset for each field, organized into a labeled dictionary that is easy to interpret. This dictionary is sent to Node-RED, where it is displayed for the PlanktoScope user, enabling seamless access to hardware details in a clear format.

## Edit eeprom operation
The *edit operation* on the EEPROM allows the update of a specific field without affecting other data stored nearby. When an edit request is received, the field is identified by its key, and the program accesses its corresponding start address and reserved memory size to update it in the correct EEPROM memory space. By positioning each edit operation within these bounds, the EEPROM ensures data integrity, preventing overlap with adjacent fields.

To prevent residual data from a previous entry (especially if the new entry is shorter than the previous one), the information to store is padded with 0x00 to match the exact length expected by EEPROM.

```Python
    if len(data_to_write) < data_length:
            data_to_write.extend([0x00] * (data_length - len(data_to_write)))
```

 This ensures that the EEPROM memory maintains a clear, structured layout, which is critical for consistency and readability. The write method used for editing follows the same principles as the initial write operation, securing data within the assigned address ranges and preserving the organized memory structure of the EEPROM.
