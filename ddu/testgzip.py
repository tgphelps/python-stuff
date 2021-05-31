
import gzip
import os
import shutil
import time

def main() -> None:
    elapsed = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    size = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for j in range(11):
        for n in range(1, 10):
            before = time.time()
            zip_name = f'ddu.tar{n}.gz'
            with open ('ddu.tar', 'rb') as f_in, \
                 gzip.open(zip_name, 'wb', compresslevel=n) as f_out:
                shutil.copyfileobj(f_in, f_out)
            elapsed[n - 1] += time.time() - before
            size[n - 1] = os.stat(zip_name).st_size
    for j in range (9):
        print(f'level {j + 1}: elapsed {elapsed[j]}, size {size[j]}')

if __name__ == '__main__':
    main()
