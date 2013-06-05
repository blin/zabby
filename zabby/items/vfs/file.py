import hashlib

__all__ = ['md5sum', ]


def md5sum(file_path, block_size=8192):
    """
    Returns md5sum of file at file_path

    :param block_size: file will be read in chunks of this size
    """
    hash_aggregator = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(block_size)
            hash_aggregator.update(data)
            if len(data) < block_size:
                break
    return hash_aggregator.hexdigest()
