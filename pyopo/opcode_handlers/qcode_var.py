import struct
from pyopo.opl_exceptions import *

import logging
import logging.config

from pyopo.heap import data_stack
from pyopo.var_stack import stack

from pyopo.loader import loader

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()
# _logger.setLevel(logging.DEBUG)

# Precompile struct bytepack formats
STRUCT_FORMAT_UINT16 = struct.Struct("<H")
STRUCT_FORMAT_INT16 = struct.Struct("<h")


def qcode_push_var(procedure, data_stack: data_stack, stack: stack):
    dsf_offset = procedure.data_stack_frame_offset + procedure.read_qcode_uint16()

    op_code = procedure.get_executed_opcode()
    assert op_code >= 0 and op_code < 4

    value = data_stack.read(op_code, dsf_offset)

    _logger.debug(
        f"{hex(op_code)} - push+ {value} of Type: {op_code} at LL+ DSF Offset: {dsf_offset}"
    )

    stack.push(op_code, value)


def qcode_push_addr_array(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push+ the addr of LL+(pop%)")

    array_type = procedure.get_executed_opcode() - 0x14

    offset = procedure.read_qcode_uint16()
    dsf_offset = procedure.data_stack_frame_offset + offset
    array_index = stack.pop() - 1  # OPL indexes start at 1

    if array_type == 0:
        # Word Array
        dsf_offset += 2 * array_index
    elif array_type == 1:
        # Long Array
        dsf_offset += 4 * array_index
    elif array_type == 2:
        # Float Array
        dsf_offset += 8 * array_index
    elif array_type == 3:
        # String Array

        # Determine string length from the procedure string section
        for declared_string in procedure.procedure["string_declarations"]:
            if declared_string["data_stack_frame_offset"] == offset - 1:
                dsf_offset += (
                    declared_string["length"] + 1
                ) * array_index  # QStrs have length byte too
                break
        else:
            raise ("Unable to determine string length")

    # print(f" - Type: {array_type} at DSF Offset: {dsf_offset} Array Offset: {array_index}")

    stack.push(4, dsf_offset)


def qcode_push_addr_field(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(
        f"{hex(procedure.get_executed_opcode())} - push= the address of field pop$+ of data file D"
    )

    array_type = procedure.get_executed_opcode() - 0x24

    d = procedure.read_qcode_byte()  # DBF D Byte

    var_name = stack.pop()

    dsf_offset = -1
    for database in procedure.executable.databases:
        if database["d"] == d:
            for i in range(len(database["vars"])):
                if database["vars"][i][1] == var_name:
                    # Found var, calculate psuedo address
                    # Database addreses are beyond regular addrs
                    dsf_offset = 1024 * 1024 + 1024 * d + i
                    break

    if dsf_offset == -1:
        raise ("Error finding var ref")

    _logger.info(f" - Calculated Pseudo DSF offset for Database = {dsf_offset}")
    stack.push(4, dsf_offset)


def qcode_push_value_field(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(
        f"{hex(procedure.get_executed_opcode())} - push= the value of field pop$+ of data file D"
    )

    d = procedure.read_qcode_byte()  # DBF D Byte

    var_name = stack.pop()

    found_db_field = False
    for database in procedure.executable.databases:
        if database["d"] == d:
            _logger.debug(f"Found DB: {d}")
            for i in range(len(database["vars"])):
                if database["vars"][i][1] == var_name:
                    _logger.debug("Found DB Field Var")
                    db_field_val = database["handler"].current_record[
                        database["vars"][i][1]
                    ]
                    db_field_type = database["vars"][i][0]

                    _logger.debug(
                        f"Found DB Field Var {var_name} of value {db_field_val} of type {db_field_type}"
                    )

                    stack.push(db_field_type, db_field_val)
                    found_db_field = True
                    break

    if not found_db_field:
        # _logger.warning(f"DB {d} var name: {var_name} Field not found")
        raise ("DB Field var not found")


def qcode_push_var_array(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(
        f"{hex(procedure.get_executed_opcode())} - push+ the value of LL+(pop%)"
    )

    array_type = procedure.get_executed_opcode() - 0x10

    offset = procedure.read_qcode_uint16()
    dsf_offset = procedure.data_stack_frame_offset + offset
    array_index = stack.pop() - 1  # OPL Indexes start at 1

    _logger.debug(
        f"Type: {array_type} at DSF Offset: {dsf_offset} Array Offset: {array_index}"
    )

    if array_type == 0:
        # Word Array
        dsf_offset += 2 * array_index
    elif array_type == 1:
        # Long Array
        dsf_offset += 4 * array_index
    elif array_type == 2:
        # Float Array
        dsf_offset += 8 * array_index
    elif array_type == 3:
        # String Array

        for declared_string in procedure.procedure["string_declarations"]:
            if declared_string["data_stack_frame_offset"] == offset - 1:
                dsf_offset += (
                    declared_string["length"] + 1
                ) * array_index  # QStrs have length byte too
                break
        else:
            raise ("Unable to determine string length")

    value = data_stack.read(array_type, dsf_offset)
    # print(f" - Value: {value} of Type: {array_type} at DSF Offset: {dsf_offset} Array Offset: {array_index}")

    stack.push(array_type, value)


def qcode_push_addr(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"{hex(procedure.get_executed_opcode())} - push= the address of LL+")

    dsf_offset = procedure.data_stack_frame_offset + procedure.read_qcode_uint16()

    _logger.debug(f" -  DSF Offset: {dsf_offset}")

    stack.push(4, dsf_offset)  # Push


def qcode_uadd(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x50 - push= UADD pop%2 pop%1")

    # Convert INT16 vals to UINT16
    y = STRUCT_FORMAT_UINT16.unpack_from(STRUCT_FORMAT_INT16.pack(stack.pop()))[0]
    x = STRUCT_FORMAT_UINT16.unpack_from(STRUCT_FORMAT_INT16.pack(stack.pop()))[0]
    stack.push(0, x + y)


def qcode_usub(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x51 - push= USUB pop%2 pop%1")

    # Convert INT16 vals to UINT16
    y = STRUCT_FORMAT_UINT16.unpack_from(STRUCT_FORMAT_INT16.pack(stack.pop()))[0]
    x = STRUCT_FORMAT_UINT16.unpack_from(STRUCT_FORMAT_INT16.pack(stack.pop()))[0]
    stack.push(0, x - y)


def qcode_push_vv_plus(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"{hex( procedure.get_executed_opcode())} - push+ VV+")

    stack_type = procedure.get_executed_opcode() - 0x28
    pc = procedure.get_program_counter()

    if stack_type == 0:
        # Int16 - Word
        stack_val = procedure.read_qcode_int16()
    elif stack_type == 1:
        # Int32 - Long
        stack_val = struct.unpack_from("<i", procedure.procedure["qcode"], pc)[0]
        procedure.set_program_counter_delta(4)
    elif stack_type == 2:
        # Float
        stack_val = struct.unpack_from("<d", procedure.procedure["qcode"], pc)[0]
        procedure.set_program_counter_delta(8)
    elif stack_type == 3:
        # String
        stack_val = loader._read_qstr(pc, procedure.procedure["qcode"])
        _logger.info(f"VV+ value: {stack_type} {len(stack_val)} {stack_val}")
        procedure.set_program_counter_delta(len(stack_val) + 1)
    else:
        raise ("Invalid VV opcode type")

    # print(f" -  Stack Type: {stack_type} Value: {stack_val}")

    stack.push(stack_type, stack_val)  # Push


def qcode_push_vv_long(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push& VV!")

    vv_val_byte = procedure.read_qcode_byte()

    vv_val = vv_val_byte
    if vv_val >= 0x80:
        # Convert to minus
        vv_val += 0xFFFFFF00

    # Convert UInt32 to Int32
    vv_val = struct.unpack("<i", struct.pack("<I", vv_val))[0]

    # print(f" -  push& {vv_val} VV! {vv_val_byte}")

    stack.push(1, vv_val)  # Push


def qcode_push_vv_word_to_long(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"{hex(procedure.get_executed_opcode())} - push& VV%")

    vv_val_raw = procedure.read_qcode_uint16()

    vv_val = vv_val_raw
    if vv_val >= 0x8000:
        # Convert to minus
        vv_val += 0xFFFF0000

    # Convert UInt32 to Int32
    vv_val = struct.unpack("<i", struct.pack("<I", vv_val))[0]

    # print(f" -  push& {vv_val} VV% {vv_val_raw}")

    stack.push(1, vv_val)  # Push


def qcode_push_vv_word(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x4F - push% VV! ($80 to $FF convert to $FF80 to $FFFF)")

    # Takes a byte and returns a Word
    vv_val_byte = procedure.read_qcode_byte()

    vv_val = vv_val_byte
    if vv_val >= 0x80:
        # Convert to minus
        vv_val += 0xFF00

    # Convert UInt16 to Int16
    vv_val = STRUCT_FORMAT_INT16.unpack(STRUCT_FORMAT_UINT16.pack(vv_val))[0]

    _logger.debug(f"push% {vv_val} VV! {vv_val_byte}")

    stack.push(0, vv_val)  # Push Word


def qcode_store_pop1_in_pop2(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - store pop+1 in location with address pop=2")

    stack_type = procedure.get_executed_opcode() - 0x84

    stack_val = stack.pop()
    stack_addr = stack.pop()

    if stack_addr >= 1024 * 1024:
        # Database
        stack_addr -= 1024 * 1024
        d = int(stack_addr / 1024)
        field_index = stack_addr - 1024 * d

        stored = False
        for database in procedure.executable.databases:
            if database["d"] == d:
                for i in range(len(database["vars"])):
                    if i == field_index:
                        database["handler"].current_record[
                            database["vars"][i][1]
                        ] = stack_val
                        stored = True
                        _logger.debug(
                            f" - Storing {stack_val} to Database {d} field {field_index} {database['vars'][i][1]}"
                        )
                        break
                break

        if not stored:
            raise ("Error: Unable to store Field Value")

    else:
        # print(f" - Storing {stack_val} to DSF Addr {stack_addr}")
        data_stack.write(stack_type, stack_val, stack_addr)


def qcode_push_ee_addr(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push= the address of EE+ [cannot be a parameter]")

    ee_ref = procedure.read_qcode_uint16()

    # Check to see if the EE reference is already cached, to remove the lookup overhead
    dsf_offset = procedure.ee_dsf_cache.get(ee_ref, -1)

    if dsf_offset == -1:
        # Attempt to find the EE
        gd_entry = procedure.procedure["cached_gd"].get(ee_ref)
        if gd_entry:
            gd_name = gd_entry["name"]

            # Check the first instance in the DS
            for proc in procedure.executable.proc_stack:
                for gd in proc.procedure["global_declarations"]:
                    if gd["name"] == gd_name:
                        dsf_offset = (
                            proc.data_stack_frame_offset + gd["data_stack_frame_offset"]
                        )  # DSF Offset is for callee Proc
                        # print(f"Found Global Reference {gd_name} Originally declared in Stack Proc {proc.procedure['name']} at DSF Offset {dsf_offset}")
                        break

                if dsf_offset != -1:
                    break

    if dsf_offset == -1:
        gr_entry = procedure.procedure["cached_gr"].get(ee_ref)
        if gr_entry:
            gr_name = gr_entry["name"]

            # Find which procedure declared it
            for proc in procedure.executable.proc_stack:
                for gd in proc.procedure["global_declarations"]:
                    if gd["name"] == gr_name:
                        dsf_offset = (
                            proc.data_stack_frame_offset + gd["data_stack_frame_offset"]
                        )  # DSF Offset is for callee Proc
                        # print(f"Found Global Reference {gr_name} Originally declared in Stack Proc {proc.procedure['name']} at DSF Offset {dsf_offset}")
                        break

                if dsf_offset != -1:
                    break

    if dsf_offset == -1:
        raise (f"Unable to find EE value: {ee_ref}")

    # Cache the DSF offset for future use
    procedure.ee_dsf_cache[ee_ref] = dsf_offset

    # print(f" - max EE ref: {procedure.procedure['max_ee_ref']}")
    # print(f" - Storing DSF Addr {dsf_offset} of EE ref {ee_ref}")

    stack.push(4, dsf_offset)


def qcode_push_ee_value(procedure, data_stack: data_stack, stack: stack):
    # print(f"{hex(op_code)} - push+ the value of EE+")

    ee_ref = procedure.read_qcode_uint16()

    # Check to see if the EE reference is already cached, to remove the lookup overhead
    dsf_offset = procedure.ee_dsf_cache.get(ee_ref, -1)

    # Attempt to find the EE
    if dsf_offset == -1:
        gd_entry = procedure.procedure["cached_gd"].get(ee_ref)
        if gd_entry:
            gd_name = gd_entry["name"]

            # Check the first instance in the DS
            for proc in procedure.executable.proc_stack:
                for gd in proc.procedure["global_declarations"]:
                    if gd["name"] == gd_name:
                        dsf_offset = (
                            proc.data_stack_frame_offset + gd["data_stack_frame_offset"]
                        )  # DSF Offset is for callee Proc
                        # print(f"Found Global Reference {gd_name} Originally declared in Stack Proc {proc.procedure['name']} at DSF Offset {dsf_offset}")
                        break

                if dsf_offset != -1:
                    break

    if dsf_offset == -1:
        gr_entry = procedure.procedure["cached_gr"].get(ee_ref)
        if gr_entry:
            gr_name = gr_entry["name"]

            # Find which procedure declared it
            for proc in procedure.executable.proc_stack:
                for gd in proc.procedure["global_declarations"]:
                    if gd["name"] == gr_name:
                        dsf_offset = (
                            proc.data_stack_frame_offset + gd["data_stack_frame_offset"]
                        )  # DSF Offset is for callee Proc
                        # print(f"Found Global Reference {gr_name} Originally declared in Stack Proc {proc.procedure['name']} at DSF Offset {dsf_offset}")
                        break

                if dsf_offset != -1:
                    break

    if dsf_offset == -1:
        for param in procedure.procedure["parameters"]:
            if param["ee"] == ee_ref:
                # Params are read only

                # print(param)
                # print(f" - Value: { param['value']} of Type: {param['type']} at EE Ref: {ee_ref}")

                stack.push(param["type"], param["value"])
                return

    if dsf_offset == -1:
        raise (f"Unable to find EE ref: {ee_ref}")
    else:
        # Cache the DSF offset for future use (when not a param)
        procedure.ee_dsf_cache[ee_ref] = dsf_offset

    # print(f" - max EE ref: {procedure.procedure['max_ee_ref']}")
    # print(f" - Retrieving value for DSF Addr {dsf_offset} of EE ref {ee_ref}")

    ee_type = procedure.get_executed_opcode() - 0x08

    value = data_stack.read(ee_type, dsf_offset)
    _logger.debug(f" - Value: {value} of Type: {ee_type} at DSF Offset: {dsf_offset}")

    stack.push(ee_type, value)


def qcode_pop_discard(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"{hex(procedure.get_executed_opcode())} - pop+ and discard")
    stack.pop()


def qcode_push_word_pop(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"{hex(procedure.get_executed_opcode())} - push% value of pop+")
    stack.push(0, int(stack.pop()))


def qcode_push_long_pop(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"{hex(procedure.get_executed_opcode())} - push& value of pop+")
    stack.push(1, int(stack.pop()))


def qcode_push_real_pop(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(f"{hex(procedure.get_executed_opcode())} - push* value of pop+")
    stack.push(2, float(stack.pop()))


def qcode_push_ee_array_addr(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(
        f"{hex(procedure.get_executed_opcode())} - push+ the addr of EE+(pop%)"
    )

    ee_ref = procedure.read_qcode_uint16()
    array_type = procedure.get_executed_opcode() - 0x1C

    # Check to see if the EE reference is already cached when not referencing a string
    dsf_offset = -1 if array_type == 3 else procedure.ee_dsf_cache.get(ee_ref, -1)

    ref_proc = None

    # Attempt to find the EE

    if dsf_offset == -1:
        gd_entry = procedure.procedure["cached_gd"].get(ee_ref)
        if gd_entry:
            gd_name = gd_entry["name"]

            # Check the first instance in the DS
            for proc in procedure.executable.proc_stack:
                for gd in proc.procedure["global_declarations"]:
                    if gd["name"] == gd_name:
                        ref_proc = proc
                        dsf_offset = (
                            proc.data_stack_frame_offset + gd["data_stack_frame_offset"]
                        )  # DSF Offset is for callee Proc
                        _logger.debug(
                            f"Found Global Declaration {gd_name} Originally declared in Stack Proc {proc.procedure['name']} at DSF Offset {dsf_offset}"
                        )
                        break

                if dsf_offset != -1:
                    break

    if dsf_offset == -1:
        for gr in procedure.procedure["global_references"]:
            if gr["ee"] == ee_ref:
                gr_name = gr["name"]

                # Find which procedure declared it
                for proc in procedure.executable.proc_stack:
                    for gd in proc.procedure["global_declarations"]:
                        if gd["name"] == gr_name:
                            ref_proc = proc
                            dsf_offset = (
                                proc.data_stack_frame_offset
                                + gd["data_stack_frame_offset"]
                            )  # DSF Offset is for callee Proc
                            _logger.debug(
                                f"Found Global Reference {gr_name} Originally declared in Stack Proc {proc.procedure['name']} at DSF Offset {dsf_offset}"
                            )
                            break

                    if dsf_offset != -1:
                        break

                break

    if dsf_offset == -1:
        raise (f"Unable to find EE Ref: {ee_ref}")

    # Cache the DSF offset for future use
    procedure.ee_dsf_cache[ee_ref] = dsf_offset

    array_index = stack.pop() - 1  # OPL addresses start at 1

    if array_type == 0:
        # Word Array
        dsf_offset += 2 * array_index
    elif array_type == 1:
        # Long Array
        dsf_offset += 4 * array_index
    elif array_type == 2:
        # Float Array
        dsf_offset += 8 * array_index
    elif array_type == 3:
        # String Array

        for declared_string in ref_proc.procedure["string_declarations"]:
            if (
                declared_string["data_stack_frame_offset"]
                == dsf_offset - ref_proc.data_stack_frame_offset - 1
            ):
                dsf_offset += (
                    declared_string["length"] + 1
                ) * array_index  # QStrs have length byte too
                break
        else:
            raise ("Unable to determine string length")

    _logger.debug(
        f" - Storing DSF Addr {dsf_offset} of EE ref {ee_ref} ({array_index})"
    )

    stack.push(4, dsf_offset)


def qcode_addr(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x00 - push% ADDR pop=")

    # Convert from uint16 addr to int16
    # print(f" - Pushing Addr {addr} to Stack as Word")

    stack.push(0, stack.pop())  # Push Word


def qcode_addr_str(procedure, data_stack: data_stack, stack: stack):
    _logger.debug("0x57 0x1F - push% ADDR pop= (str)")

    # Convert from uint16 addr to int16
    addr = stack.pop() - 1  # String addresses having leading length byte

    _logger.debug(f" - Pushing Addr {addr} to Stack as Word")

    stack.push(0, addr)  # Push Word


def qcode_push_ee_array_val(procedure, data_stack: data_stack, stack: stack):
    _logger.debug(
        f"{hex(procedure.get_executed_opcode())} - push+ the value of EE+(pop%)"
    )

    ee_ref = procedure.read_qcode_uint16()
    array_type = procedure.get_executed_opcode() - 0x18

    # Check to see if the EE reference is already cached if its not a string
    dsf_offset = -1 if array_type == 3 else procedure.ee_dsf_cache.get(ee_ref, -1)

    ref_proc = None

    if dsf_offset == -1:
        # Attempt to find the EE
        gd_list = list(
            filter(
                lambda gd: gd["ee"] == ee_ref,
                procedure.procedure["global_declarations"],
            )
        )
        if len(gd_list) > 0:
            gd = gd_list[-1]
            gd_name = gd["name"]

            # Check the first instance in the DS
            for proc in procedure.executable.proc_stack:
                for gd in proc.procedure["global_declarations"]:
                    if gd["name"] == gd_name:
                        ref_proc = proc
                        dsf_offset = (
                            proc.data_stack_frame_offset + gd["data_stack_frame_offset"]
                        )  # DSF Offset is for callee Proc
                        _logger.debug(
                            f"Found Global Declaration {gd_name} Originally declared in Stack Proc {proc.procedure['name']} at DSF Offset {dsf_offset}"
                        )
                        break

                if dsf_offset != -1:
                    break

    if dsf_offset == -1:
        for gr in procedure.procedure["global_references"]:
            if gr["ee"] == ee_ref:
                gr_name = gr["name"]

                # Find which procedure declared it
                for proc in procedure.executable.proc_stack:
                    for gd in proc.procedure["global_declarations"]:
                        if gd["name"] == gr_name:
                            ref_proc = proc
                            dsf_offset = (
                                proc.data_stack_frame_offset
                                + gd["data_stack_frame_offset"]
                            )  # DSF Offset is for callee Proc
                            _logger.debug(
                                f"Found Global Reference!! {gr_name} Originally declared in Stack Proc {proc.procedure['name']} at DSF Offset {dsf_offset}"
                            )
                            break

                    if dsf_offset != -1:
                        break

                break

    if dsf_offset == -1:
        # _logger.warning(f'Unable to determine EE ref: {ee_ref}')
        raise (f"Unable to determine EE ref: {ee_ref}")

    # Cache the DSF offset for future use
    procedure.ee_dsf_cache[ee_ref] = dsf_offset

    array_index = stack.pop() - 1  # OPL indexes start at 1

    if array_index < 0:
        # _logger.warning(f'Error: push_ee_array_val Array Index {array_index} out of bounds!')
        raise (KErrOutOfRange)

    if array_type == 0:
        # Word Array
        dsf_offset += 2 * array_index

    elif array_type == 1:
        # Long Array
        dsf_offset += 4 * array_index
    elif array_type == 2:
        # Float Array
        dsf_offset += 8 * array_index
    elif array_type == 3:
        # String Array

        for declared_string in ref_proc.procedure["string_declarations"]:
            if (
                declared_string["data_stack_frame_offset"]
                == dsf_offset - ref_proc.data_stack_frame_offset - 1
            ):
                dsf_offset += (
                    declared_string["length"] + 1
                ) * array_index  # QStrs have length byte too
                break
        else:
            raise ("Unable to determine string length")

    ee_val = data_stack.read(array_type, dsf_offset)

    _logger.debug(
        f" - Storing Value {ee_val} DSF Addr {dsf_offset} of EE ref {ee_ref} ({array_index})"
    )

    stack.push(array_type, ee_val)
