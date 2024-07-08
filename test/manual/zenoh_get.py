import zenoh

key = "exampleapplication/company_premises"

if __name__ == "__main__":
    session = zenoh.open()
    session.get(key, lambda reply:
        print(f"Received '{reply.ok.key_expr}': '{reply.ok.payload.decode('utf-8')}'")
        if reply.ok is not None else print(f"Received ERROR: '{reply.err.payload.decode('utf-8')}'"))
