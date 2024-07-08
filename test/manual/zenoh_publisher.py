import time

import zenoh

key = "dockerContextDefinitions/company_premises"
value = "test_scope"

def increasing_values():
    session = zenoh.open()
    pub = session.declare_publisher(key)
    i = 0
    while True:
        buf = f"{i}"
        print(f"Putting Data ('{key}': '{buf}')...")
        pub.put(buf)
        i += 1
        time.sleep(1)

def single_value():
    session = zenoh.open()
    session.put(key, value)

if __name__ == "__main__":
    increasing_values()
