# app/worker.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = None
_inference_queue = None

def create_executor(max_workers=1):
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=max_workers)
    return _executor

def create_queue():
    global _inference_queue
    if _inference_queue is None:
        _inference_queue = asyncio.Queue()
    return _inference_queue

async def inference_consumer(asr_callable):
    queue = create_queue()
    executor = create_executor(1)
    loop = asyncio.get_running_loop()
    while True:
        job = await queue.get()
        try:
            fn = job['callable']
            args = job.get('args', ())
            res = await loop.run_in_executor(executor, fn, *args)
            job['future'].set_result(res)
        except Exception as e:
            job['future'].set_exception(e)
        finally:
            queue.task_done()

async def submit_job(callable_fn, *args):
    queue = create_queue()
    fut = asyncio.get_running_loop().create_future()
    await queue.put({"callable": callable_fn, "args": args, "future": fut})
    return await fut
