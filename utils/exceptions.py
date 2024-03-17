def exception_handler(e, status_code=400):
    return {
        'statusCode': status_code,
        'result': str(e)
    }