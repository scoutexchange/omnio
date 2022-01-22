def default_config():
    return {
        "file": {},
        "http": {"iter_content_chunk_size": 512},
        "s3": {
            "upload_part_size": 5 * 1024 ** 2,
            "boto_client_config_args": [],
            "boto_client_config_kwargs": {},
        },
    }
