import asyncio
import dns.resolver
from cache import DNSAnswersCache
from answer_builder_helper import *

writers = set()


class Server:
    def __init__(self):
        self.cache = DNSAnswersCache()
        self.resolver = dns.resolver.Resolver()
        self.server = None

    async def start_server(self):
        self.server = await asyncio.start_server(self.handle_echo, '127.0.0.1', 8888)
        await self.server.serve_forever()

    async def handle_echo(self, reader, writer):
        writers.add(writer)
        try:
            while True:
                request = await reader.read(1024)

                if not request:
                    writer.close()
                    writers.remove(writer)
                    print("Goodbye")
                    return

                domain, type_name, class_name = parse_request(request.decode())
                if type_name not in r_types.keys() or len(domain) == 0 or class_name != "IN":
                    writer.write("Invalid request".encode())
                    await writer.drain()
                    continue

                answer = ""
                for i in self.make_dns_answer(domain, type_name):
                    answer += i

                writer.write(answer.encode())
                await writer.drain()

        finally:
            writer.close()

    def make_dns_answer(self, domain_name, q_type):
        from_cache = self.try_load_from_cache(domain_name, q_type)
        if from_cache:
            print("cache!")
            return from_cache
        request = self.try_do_request(domain_name, q_type)
        if request:
            print("request!")
            return request
        return ["Invalid request"]

    def try_do_request(self, domain_name, q_type):
        try:
            response = self.resolver.resolve(domain_name, q_type)

            domain_name = response.qname.to_text()[:-1]
            for answer in response.response.answer:
                tll = answer.ttl
                q_class = str(dns.rdataclass.to_text(answer.rdclass))
                q_type = str(dns.rdatatype.to_text(answer.rdtype))
                result = []
                to_cache = []
                for addr in answer.items:
                    data_length = len(addr.to_wire())
                    result.append(form_answer(domain_name, q_type, q_class, addr, tll, data_length))
                    to_cache.append([q_class, str(addr), tll, data_length])
                if len(to_cache) > 0:
                    self.cache.write_answers_to_cache(domain_name, q_type, to_cache)
                return result
        except Exception as e:
            return [str(e)]
        return None

    def try_load_from_cache(self, domain_name, q_type):
        loaded = self.cache.load_answers_from_cache(domain_name, q_type)
        if len(loaded) > 0:
            result = []
            for item in loaded:
                a_class, addr, new_tll, data_length, creation_time = item
                result.append(form_answer(domain_name, q_type, a_class, addr, new_tll, data_length))
            return result
        return None


def parse_request(request: str) -> (str, str, str):
    elements = request.strip().replace(":", "").replace(",", "").split()
    if len(elements) < 5:
        return "", "", ""
    return elements[0], elements[2], elements[4]


def form_answer(domain_name, q_type, q_class, addr, tll, data_length) -> str:
    addr = str(addr)
    addr = addr[:-1] if addr[-1] == "." else addr
    return f"""{domain_name}: type {q_type}, class {q_class}, {r_small_address[q_type]} {addr}
    Name: {domain_name}
    Type: {q_type} ({r_types_names[q_type]}) ({r_types[q_type]})
    Class: {q_class} (0x0001)
    Time to live: {tll} ({format_time(tll)})
    Data length: {data_length}
    {r_address[q_type]}: {addr}\n"""


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    result = ""
    if hours > 0:
        result += f"{hours} hours, "
    if minutes > 0:
        result += f"{minutes} minutes, "

    return result + f"{seconds} seconds"


async def main():
    server = Server()
    await server.start_server()


if __name__ == "__main__":
    asyncio.run(main())
