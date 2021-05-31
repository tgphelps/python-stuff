
DISK = 'data/testdisk'


def main():
    with open(DISK, 'wb') as f:
        for n in range(100):
            for i in range(28):
                f.write(bytes([n]))


if __name__ == '__main__':
    main()
