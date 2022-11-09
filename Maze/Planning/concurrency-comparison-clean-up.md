
### asyncio

- Future is `await`ed
- Futures can be `await`ed in parallel to run `n` coroutines
- Top-level tasks are run referee, and run observers
  - Con: Intermediate steps need to be declared async and awaited too (`setup`, `take_turn`, `win`)
  await task
  - Con: Busy loop or very inefficient strategy can block everything

### concurrent.futures

- Future is retrieved with `.result()`
- Futures can be created by `ThreadPoolExecutor.submit()`
- A list of futures can be awaited with `.as_completed()`
- Con: Extra architecture to "submit" a task to the main thread
  - Our task to actually submit is `shared_queue.put(observer_update)`
- Con: Ctrl+C needs explicit handling so that all threads are killed

