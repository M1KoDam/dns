# dns
DNS server and client providing the ability to receive responses to DNS queries, as in Wireshark

### Сделал:
1. Обработка нескольких клиентов
2. Сохранение сервером запросов в кэш и возвращение их с учётом TTL
3. Сохранение кэша при закрытии сервера
4. Также сервер в консоли сообщает - делал ли он запрос или же взял из кэша

Для выхода клиенту достаточно ввести пустую строку или одно из слов: exit или stop

P.S. Special thx to WireShark!