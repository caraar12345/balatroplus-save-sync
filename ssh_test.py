import argparse
import tempfile

import fabric


def main():
    parser = argparse.ArgumentParser(description="Process SSH connection details.")
    parser.add_argument("--host", required=True, help="The Mac's IP or hostname")
    parser.add_argument("--username", required=True, help="The username for SSH")
    parser.add_argument(
        "--ssh-key", required=True, help="The location of the SSH private key"
    )

    args = parser.parse_args()

    with tempfile.TemporaryFile(mode="w+b") as temp:
        ssh_conn = fabric.Connection(
            host=args.host,
            user=args.username,
            connect_kwargs={"key_filename": args.ssh_key},
        )
        temp.write(args.ssh_key.encode())
        temp.seek(0)
        print(temp.read().decode())
    print(f"Device: {args.host}")
    print(f"Username: {args.username}")
    print(f"SSH Key Location: {args.ssh_key}")


if __name__ == "__main__":
    main()
