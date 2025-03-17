import zenoh, time

def listener(sample):
    print(f"Received {sample.kind} ('{sample.key_expr}': '{sample.payload}')")

if __name__ == "__main__":
    session = zenoh.open()
    sub = session.declare_subscriber('dockerContextDefinitions/group', listener)
    time.sleep(60)
