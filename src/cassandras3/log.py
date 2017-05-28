import logging

logger = logging.getLogger('cassandras3')


def setup_logging(level=logging.DEBUG):  # pragma: no cover
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    logger.setLevel(level)
    return logger
