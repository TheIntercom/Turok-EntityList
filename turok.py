import pymem
import csv
from datetime import datetime

p = pymem.Pymem('sobek.exe')

sobek = pymem.process.module_from_name(p.process_handle, 'sobek.exe')

sobek_base = sobek.lpBaseOfDll
player_offset = int('390CF4', 16)
player_address = p.read_int(sobek_base + player_offset)

magic_start = int('0078E3E8', 16)

prev_ent = p.read_int(player_address + 4) - 4
next_ent = p.read_int(player_address + 8) - 4

counter = 0

# ###############################################################################################################################
# Wrong prev always seems to be 0x0078e3e8
# Wrong next has inconsistent offset from last ent base between loads, need more info
#   Last ent always seems to be the ChronoScepter so I can guess I can check for that
# ###############################################################################################################################

current_ent = player_address

prev_ent_buffer = 0
next_ent_buffer = 0

start = 0
end = 0

debug = False

while (prev_ent != magic_start):
    try:
        prev_ent = p.read_int(current_ent + 4) - 4

        prev_ent_buffer = current_ent
        current_ent = prev_ent
    except Exception as e:
        print(f'broke:{e}')

start = prev_ent_buffer

s = f'First Ent: {prev_ent_buffer:08X} -- Broken Prev Ent: {prev_ent:08X}'

print('-' * len(s))
print(s)
print('-' * len(s))

current_ent = start

with open(f'log-{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv', mode='w', newline = '') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    while True:
        counter += 1

        try:
            current_ent_id = p.read_int(current_ent + 64)
            current_ent_health = p.read_int(current_ent + 224)
            current_ent_type_subclass = p.read_int(current_ent + 216)
            current_ent_type_name = p.read_string(current_ent_type_subclass + 16, 32)

            prev_ent = p.read_int(current_ent + 4) - 4
            next_ent = p.read_int(current_ent + 8) - 4

            csv_writer.writerow([f'0x{prev_ent:08X}',
                                f'0x{current_ent:08X}',
                                f'0x{next_ent:08X}',
                                current_ent_id,
                                current_ent_health,
                                current_ent_type_name])

            print(f'{counter} | {prev_ent:08X} <- {current_ent:08X} -> {next_ent:08X} | id:{current_ent_id} | hp:{current_ent_health} | type:{current_ent_type_name}')

            next_ent_buffer = current_ent
            current_ent = next_ent
        except Exception as e:
            if debug:
                print(f'broke:{e}')
            break

end = next_ent_buffer

s = f'Last Ent: {next_ent_buffer:08X} -- Broken Next Ent: {next_ent:08X}'

print('-' * len(s))
print(s)
print('-' * len(s))
print(f'Count :{counter} -- Start: {start:08X} -- End: {end:08X}')
print('-' * len(s))
