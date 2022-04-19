from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import socket


class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} updated")
        for ip in info.addresses:
            print('IP ADDRESS: ', end='')
            print(socket.inet_ntoa(ip))
        print('PORT: ', end='')
        print(info.port)
        status_options = info.properties[b'STATUS']
        color_options = info.properties[b'COLOR']
        intensity_options = info.properties[b'INTENSITY']
        print('LED STATUS OPTIONS: ', end='')
        print(status_options.decode('utf-8'))
        print('LED COLOR OPTIONS: ', end='')
        print(color_options.decode('utf-8'))
        print('LED INTENSITY OPTIONS: ', end='')
        print(intensity_options.decode('utf-8'))

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} added, service info: {info}")
        for ip in info.addresses:
            print('IP ADDRESS: ', end='')
            print(socket.inet_ntoa(ip))
        print('PORT: ', end='')
        print(info.port)
        status_options = info.properties[b'STATUS']
        color_options = info.properties[b'COLOR']
        intensity_options = info.properties[b'INTENSITY']
        print('LED STATUS OPTIONS: ', end='')
        print(status_options.decode('utf-8'))
        print('LED COLOR OPTIONS: ', end='')
        print(color_options.decode('utf-8'))
        print('LED INTENSITY OPTIONS: ', end='')
        print(intensity_options.decode('utf-8'))


zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_LED._tcp.local.", listener)
try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()