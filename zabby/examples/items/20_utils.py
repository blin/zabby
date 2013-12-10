# from zabby.core.six import b
# from zabby.core.exceptions import OperatingSystemError
# from zabby.core.utils import sh, exception_guard, tcp_communication
# from zabby.compatability import userparameter_to_key_and_command
# import os
# def redis_ping():
#     responses = tcp_communication(6379, requests=[b('ping\r\n')])
#     got_pong = b('+PONG\r\n') in responses
#     return int(got_pong)


# def convert_userparameters(dir):
#     userparameter_files = [os.path.join(dir, f) for f in os.listdir(dir)]
#     userparameters = dict()
#     for file_name in userparameter_files:
#         with open(file_name) as f:
#             for line in f:
#                 key, command = userparameter_to_key_and_command(line)
#                 userparameters[key] = sh(command)
#     return userparameters


items = {
    # 'cat': sh('cat {0}'),
    # 'sleep': exception_guard(sh('sleep 1; echo 1', timeout=0.5),
    #                          OperatingSystemError, 0),
    # 'redis.ping': exception_guard(redis_ping, IOError, 0)
}

# items.update(convert_userparameters('/etc/zabbix/zabbix_agentd.d/'))
