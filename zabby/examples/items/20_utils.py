# from zabby.core.six import b
# from zabby.core.exceptions import OperatingSystemError
# from zabby.core.utils import sh, exception_guard, tcp_communication


# def redis_ping():
#     responses = tcp_communication(6379, requests=[b('ping\r\n')])
#     got_pong = b('+PONG\r\n') in responses
#     return int(got_pong)


items = {
    # 'cat': sh('cat {0}'),
    # 'sleep': exception_guard(sh('sleep 1; echo 1', timeout=0.5),
    #                          OperatingSystemError, 0),
    # 'redis.ping': exception_guard(redis_ping, IOError, 0)
}
