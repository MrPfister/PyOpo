import os
import json
import struct                                                       
import sys

import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)

# Improve _logger performance
logging._srcfile = None
logging.logThreads = False
logging.logProcesses = False
logging.logMultiprocessing = False

import pyopo

class loader:
    first_proc = True

    @staticmethod
    def load_executable(
        file: str
    ):

        binary = None
        with open(file,"rb") as f:
            binary = f.read()

        header = loader._readheader(binary)

        embedded_files = []
        embedded_files_offset = 20 + 1 + len(header["source_filename"])
        if header["second_header_offset"] != embedded_files_offset:
            # If the Second Header Offset is more than offset 20 + QStr, then there is embedded files
            print(f'{embedded_files_offset} vs {header["second_header_offset"]}')
            embedded_files = loader._readembeddedfiles(binary, embedded_files_offset, header["second_header_offset"])

        procedure_table = loader._read_procedure_table(header["procedure_table_offset"], header["translator_version"], binary, file)

        return pyopo.executable(file, binary, header, procedure_table, embedded_files)
    
    def _readembeddedfiles(
        binary: bytes,
        embedded_files_offset: int,
        second_header_offset: int
    ) -> list:
         
        file_offset = embedded_files_offset

        embedded_files = []

        while file_offset < second_header_offset:
            file_len = struct.unpack_from("<H", binary, file_offset)[0]
            file_offset += 2

            embedded_file_info = {
                'start_offset': file_offset,
                'end_offset': file_offset + file_len
            }

            if binary[file_offset:file_offset + 3].decode("utf-8", "replace") == "PIC":
                embedded_file_info['type'] = 'PIC'
            elif file_len == 36:
                # OPA Header Info
                embedded_file_info['type'] = 'OPA'
            else:
                embedded_file_info['type'] = '???'

            embedded_files.append(embedded_file_info)
            file_offset += file_len
             
        print(f"{len(embedded_files)} Embedded file(s) found")
        print(json.dumps(embedded_files, indent=4))

        return embedded_files

    def _readheader(
        binary: bytes
    ):

        header = {}

        header["filetype"] = binary[0:15].decode()
        if header["filetype"] != "OPLObjectFile**":
            print(binary[0:15].decode())
            raise ImportError("Not a valid executable")

        # First Header
        header["opo_version"] = struct.unpack_from("<H", binary, 16)[0] # OPO Version (1 - Currently ignored)
        header["second_header_offset"] = struct.unpack_from("<H", binary, 18)[0]
        header["source_filename"] = loader._read_qstr(20, binary)

        second_header = struct.unpack_from("<IHHI", binary, header["second_header_offset"])

        # Second Header
        header["file_length"] = second_header[0]
        header["translator_version"] = second_header[1]
        header["required_runtime_version"] = second_header[2]
        header["procedure_table_offset"] = second_header[3]

        return header

    def _read_procedure_table(
        procedure_table_offset: int,
        translator_version: int,
        binary,
        src_filename: str
    ):
        procedures = []

        binary_offset = procedure_table_offset

        while True:
            procedure_name = loader._read_qstr(binary_offset, binary)
            if len(procedure_name) == 0:
                # End of Procedure table
                break

            binary_offset += len(procedure_name) + 1
            proc_info = struct.unpack_from("<IH", binary, binary_offset)
            binary_offset += 6

            procedure_entry = {
                "name": procedure_name,
                "src_file": src_filename, # Store the source filename to aid loadm
                "proc_offset": proc_info[0],
                "line_no": proc_info[1]
            }

            proc_body = loader._read_procedure(procedure_entry["proc_offset"], translator_version, binary)

            procedure_entry = {**procedure_entry, **proc_body}

            procedures.append(procedure_entry)

        binary_offset += 2 # QStr + 0 byte to mark end of Procedure Table

        #print(json.dumps(procedures, indent=4))

        return procedures

    def _read_procedure(
        offset:int,
        translator_version:int,
        binary
    ):

        procedure_info = {}
        binary_offset = offset

        external_ref_counter = 18 # The first item is always 18

        # Optimisation Section (for select compiler versions)
        if translator_version >= 4383:
            procedure_info["optimisation_section_size"] = struct.unpack_from("<H", binary, binary_offset)[0]
            binary_offset += 2

        # Space Control Section
        space_control_section = struct.unpack_from("<HHH", binary, binary_offset)
        procedure_info["data_stack_frame_size"] = space_control_section[0]
        procedure_info["qcode_len"] = space_control_section[1]
        procedure_info["dynamic_stack_usage"] = space_control_section[2]
        binary_offset += 6

        # Parameters Section
        procedure_info["parameter_count"] = int(binary[binary_offset])
        binary_offset += 1
        procedure_info["parameters"] = []
        for i in range(procedure_info["parameter_count"]):
            # Parameters are given in REVERSE ORDER
            procedure_info["parameters"].append({'type': int(binary[binary_offset])})
            binary_offset += 1

        # Global Declaration Section
        section_start_offset = binary_offset
        procedure_info["global_declaration_section_size"] = struct.unpack_from("<H", binary, binary_offset)[0]
        binary_offset += 2
        procedure_info["global_declarations"] = []
        if procedure_info["global_declaration_section_size"] > 0:
            while True:
                # Global per-variable block
                global_var = {}
                global_var["name"] = loader._read_qstr(binary_offset, binary)
                binary_offset += len(global_var["name"]) + 1
                global_meta = struct.unpack_from("<BH", binary, binary_offset)
                binary_offset += 3
                global_var["type"] = global_meta[0]


                global_var["data_stack_frame_offset"] = global_meta[1] # Turn this into a virtual address

                global_var["ee"] = external_ref_counter
                external_ref_counter += len(global_var["name"]) + 4

                procedure_info["global_declarations"].append(global_var)


                if binary_offset > section_start_offset + procedure_info["global_declaration_section_size"]:
                    break

        # Called Procedure Section
        section_start_offset = binary_offset
        procedure_info["called_procedure_section_size"] = struct.unpack_from("<H", binary, binary_offset)[0]
        binary_offset +=2
        procedure_info["called_procedures"] = []
        if procedure_info["called_procedure_section_size"] > 0:
            while True:
                called_procedure = {}
                called_procedure["name"] = loader._read_qstr(binary_offset, binary)
                binary_offset += len(called_procedure["name"]) + 1
                called_procedure["argument_count"] = int(binary[binary_offset])
                binary_offset += 1

                called_procedure["ee"] = external_ref_counter
                external_ref_counter += len(called_procedure["name"]) + 2

                procedure_info["called_procedures"].append(called_procedure)
                
                if binary_offset >section_start_offset + procedure_info["called_procedure_section_size"]:
                    break

        # Global References Section
        procedure_info["global_references"] = []
        while True:
            global_name = loader._read_qstr(binary_offset, binary)
            binary_offset += len(global_name) + 1

            if len(global_name) == 0:
                # End of Section
                break

            type_code = int(binary[binary_offset])
            binary_offset += 1
            procedure_info["global_references"].append({
                "name": global_name,
                "type": type_code
            })

        if loader.first_proc:
            print(json.dumps(procedure_info['global_references'], indent=4))

        # String Control Section
        procedure_info["string_declarations"] = []
        while True:
            dsf_offset = struct.unpack_from("<H", binary, binary_offset)[0]
            binary_offset += 2
            if dsf_offset == 0:
                break
            
            string_length = int(binary[binary_offset])
            binary_offset += 1
            procedure_info["string_declarations"].append({
                "data_stack_frame_offset": dsf_offset,
                "length": string_length
            }) 

        # Array Control Section
        procedure_info["array_declarations"] = []
        while True:
            dsf_offset = struct.unpack_from("<H", binary, binary_offset)[0]
            binary_offset += 2
            if dsf_offset == 0:
                break
            
            array_length = struct.unpack_from("<H", binary, binary_offset)[0]
            binary_offset += 2
            procedure_info["array_declarations"].append({
                "data_stack_frame_offset": dsf_offset,
                "length": array_length
            })

        # Update removing EE Refs
        for i in range(procedure_info["parameter_count"]-1, -1, -1): # EE Refs are assigned IN ORDER
            procedure_info["parameters"][i]['ee'] = external_ref_counter
            external_ref_counter += 2

        for i in range(len(procedure_info["global_references"])):
            procedure_info["global_references"][i]['ee'] = external_ref_counter
            external_ref_counter += 2

        # Create optimised LUTs to allow O(1) lookup based on ee
        procedure_info["cached_gr"] = {}
        for gr_entry in procedure_info["global_references"]:
            procedure_info["cached_gr"][gr_entry['ee']] = gr_entry
            
        procedure_info["cached_cp"] = {}
        for cp_entry in procedure_info["called_procedures"]:
            procedure_info["cached_cp"][cp_entry['ee']] = cp_entry
            
        procedure_info["cached_gd"] = {}
        for gd_entry in procedure_info["global_declarations"]:
            procedure_info["cached_gd"][gd_entry['ee']] = gd_entry

        if loader.first_proc:
            loader.first_proc = False

        procedure_info["max_ee_ref"] = external_ref_counter
        procedure_info["qcode"] = binary[binary_offset:binary_offset + procedure_info["qcode_len"]]

        return procedure_info

    
    def _read_qstr(
        offset:int,

        buffer
    ) ->str:

        l = buffer[offset]
        if l == 0:
            return ""

        return buffer[offset+1:offset+1+l].decode("ascii", "replace")