import asyncio


async def main():
    print("Request example:\n"
          "yandex.ru: type A, class IN\n"
          "edge.microsoft.com: type CNAME, class IN\n"
          "google.com: type AAAA, class IN")
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    while True:
        message = input(">>> ")
        writer.write(message.encode())
        await writer.drain()
        if len(message) == 0 or message in ["stop", "exit"]:
            print("Goodbye")
            writer.close()
            await writer.wait_closed()
            return

        data = await reader.read(4096)
        print(data.decode())
        # await read_data(reader)


async def read_data(reader):
    while True:
        data = await reader.read(1024)
        if not data:
            print("exit")
            return
        print(data.decode())


if __name__ == "__main__":
    asyncio.run(main())
