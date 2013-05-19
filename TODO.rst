After dropping python 2.6
-------------------------
- Replace assert_raises calls with context management
- Replace namedtuple._asdict() with vars(namedtuple)
- Replace set([]) with set literal

After dropping everything under python 3.3
------------------------------------------
- Replace Popen(...).poll() with Popen(...).communicate(timeout=timeout)

After dropping everything under python 3.2
------------------------------------------
Replace socket.create_connection calls with context management

After dropping everything under python 3.1
------------------------------------------
Dispose of zabby.core.six

Sometime
--------
RuntimeWarning: Parent module not found while handling absolute import
