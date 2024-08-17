import os

import sh

from WASMixer import WASMixer


def obfuscate_benchmark_flatten():
    g = os.walk(r"../benchmark/basic-algorithms/flatten")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.code_flatten()
                obfuscator.wasm_binary.emit_binary()


def obfuscate_benchmark_alias_disruption():
    g = os.walk(r"../benchmark/basic-algorithms/alias_disruption")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.alias_disruption()
                obfuscator.wasm_binary.emit_binary()


def obfuscate_benchmark_nameOB():
    g = os.walk(r"../benchmark/basic-algorithms/nameOB")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.name_obfuscation()
                obfuscator.wasm_binary.emit_binary()


def obfuscate_benchmark_memoryOB():
    g = os.walk(r"../benchmark/basic-algorithms/memoryOB")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.memory_obfuscation(key=0)
                obfuscator.wasm_binary.emit_binary()


def manticore_flatten():
    g = os.walk(r"../benchmark/GillianC")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.code_flatten()
                obfuscator.wasm_binary.emit_binary()


def manticore_alias_disruption():
    g = os.walk(r"../benchmark/GillianC")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.alias_disruption()
                obfuscator.wasm_binary.emit_binary()


def manticore_memoryOB():
    g = os.walk(r"../benchmark/GillianC")
    # 平坦化，算随机数
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.memory_obfuscation(key=0)
                obfuscator.wasm_binary.emit_binary()


def manticore_nameOB():
    g = os.walk(r"../benchmark/GillianC")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.name_obfuscation()
                obfuscator.wasm_binary.emit_binary()


def manticore_btree_flatten():
    g = os.walk(r"../benchmark/btree_manticore")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.code_flatten()
                obfuscator.wasm_binary.emit_binary()


def manticore_btree_alias_disruption():
    g = os.walk(r"../benchmark/btree_manticore")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.alias_disruption()
                obfuscator.wasm_binary.emit_binary()


def btree_flatten():
    g = os.walk(r"../benchmark/btree")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.code_flatten(split_num=2, collatz=True)
                obfuscator.wasm_binary.emit_binary()

                wasm2wat = sh.Command('wasm2wat')
                flag = [wasm_path, "-o", wasm_path.split(".wasm")[0] + ".wat"]
                wasm2wat(flag)

                with open(wasm_path.split(".wasm")[0] + ".wat", "r+") as wat_file, open(
                        wasm_path.split(".wasm")[0] + "_main.wat", "r+") as wat_main_file, open(
                    wasm_path.split(".wasm")[0] + ".wast", "r+") as wast_file:
                    wat_text = wat_file.read()
                    wat_main_text = wat_main_file.read()
                    insert_location = wat_text.index("(memory")
                    wat_text = wat_text[:insert_location] + wat_main_text[:wat_main_text.index("(invoke")] + wat_text[
                                                                                                             insert_location:] + "(invoke \"main\")"
                    wast_file.seek(0)
                    wast_file.truncate()
                    wast_file.write(wat_text)


def btree_nameOB():
    g = os.walk(r"../benchmark/btree")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.name_obfuscation()
                obfuscator.wasm_binary.emit_binary()


def btree_memoryOB():
    g = os.walk(r"../benchmark/btree")
    # 平坦化，算随机数
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.memory_obfuscation(key=0)
                obfuscator.wasm_binary.emit_binary()


def btree_alias_disruption():
    g = os.walk(r"../benchmark/btree")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.alias_disruption(True)
                obfuscator.wasm_binary.emit_binary()

                wasm2wat = sh.Command('wasm2wat')
                flag = [wasm_path, "-o", wasm_path.split(".wasm")[0] + ".wat"]
                wasm2wat(flag)

                with open(wasm_path.split(".wasm")[0] + ".wat", "r+") as wat_file, open(
                        wasm_path.split(".wasm")[0] + "_main.wat", "r+") as wat_main_file, open(
                    wasm_path.split(".wasm")[0] + ".wast", "r+") as wast_file:
                    wat_text = wat_file.read()
                    wat_main_text = wat_main_file.read()
                    insert_location = wat_text.index("(memory")
                    wat_text = wat_text[:insert_location] + wat_main_text[:wat_main_text.index("(invoke")] + wat_text[
                                                                                                             insert_location:] + "(invoke \"main\")"
                    wast_file.seek(0)
                    wast_file.truncate()
                    wast_file.write(wat_text)


def realworld_flatten():
    g = os.walk(r"../benchmark/realworld_program/flatten")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.code_flatten()
                obfuscator.wasm_binary.emit_binary()


def realworld_flatten_collatz2():
    g = os.walk(r"../benchmark/realworld_program/flatten_O1")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.code_flatten(split_num=2, collatz=True)
                obfuscator.wasm_binary.emit_binary()


def realworld_alias_disruption():
    g = os.walk(r"../benchmark/realworld_program/callindirect")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.alias_disruption()
                obfuscator.wasm_binary.emit_binary()


def realworld_alias_disruption_collatz():
    g = os.walk(r"../benchmark/realworld_program/callindirect_O1")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.alias_disruption(True)
                obfuscator.wasm_binary.emit_binary()


def realworld_nameOB():
    g = os.walk(r"../benchmark/realworld_program/nameOB")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.name_obfuscation()
                obfuscator.wasm_binary.emit_binary()


def realworld_memoryOB():
    g = os.walk(r"../benchmark/realworld_program/memoryOB")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.memory_obfuscation(key=0)
                obfuscator.wasm_binary.emit_binary()


def mining_memory_obfuscation():
    g = os.walk(r"../benchmark/mining_programs")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.memory_obfuscation()
                obfuscator.wasm_binary.emit_binary()


def mining_name_obfuscation():
    g = os.walk(r"../benchmark/mining_programs")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.name_obfuscation()
                obfuscator.wasm_binary.emit_binary()


def mining_name_memory_obfuscation():
    g = os.walk(r"../benchmark/mining_programs")
    # 平坦化，算随机数
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.memory_obfuscation(key=0)
                obfuscator.name_obfuscation()
                obfuscator.wasm_binary.emit_binary()


def mining_flatten():
    g = os.walk(r"../benchmark/mining_programs")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.code_flatten()
                obfuscator.wasm_binary.emit_binary()


def mining_call():
    g = os.walk(r"../benchmark/mining_programs")
    for path, dir_list, file_list in g:
        for dir_name in file_list:
            wasm_path = os.path.join(path, dir_name)
            if wasm_path.split(".")[-1] == "wasm":
                obfuscator = WASMixer(wasm_path)
                obfuscator.alias_disruption()
                obfuscator.wasm_binary.emit_binary()


if __name__ == "__main__":
    obfuscate_benchmark_flatten()
    obfuscate_benchmark_alias_disruption()
    obfuscate_benchmark_nameOB()
    obfuscate_benchmark_memoryOB()