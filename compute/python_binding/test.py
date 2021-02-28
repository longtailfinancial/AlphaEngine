import asyncio
import ack

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
server = loop.run_until_complete(main())

async def main():
    print('Hello ...')
    await asyncio.sleep(1)
    await ack.call_rust_sleep()
    print('... World!')


