from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


def run_service(func, **kwargs):
    pool = ThreadPoolExecutor(1)
    future = pool.submit(func, **kwargs)
    pool.shutdown(wait=False)

    return future


def run_service_done(future, job):
    job.end_time = datetime.now()
    job.status = 'Done'
    if future.exception():
        job.is_success = False
        job.message = 'The job is failed: {}'
    elif future.cancelled():
        job.is_success = False
        job.message = 'The job is cancelled.'
    elif future.result():
        result = future.result()
        if result['success'] == 'True':
            job.is_success = True
            job.message = result['message']
        else:
            job.is_success = False
            job.message = 'The job is failed: {}'.format(result['message'])

    job.save()
