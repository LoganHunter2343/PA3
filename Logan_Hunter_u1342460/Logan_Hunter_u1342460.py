import subprocess
import time
import sys

def run(cmd, capture=False):
        print(f"> {cmd}")
        if capture:
                return subprocess.check_output(cmd, shell=True).decode().strip()
        else:
                subprocess.run(cmd, shell=True, check=True)

def set_costs(path):
        print(f"Switching traffic to {path} path")

        if path == "south":
                # Disable Northern path
                run("docker exec r1 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 65000' -c 'end' -c 'write'")
                run("docker exec r2 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 65000' -c 'end' -c 'write'")
                run("docker exec r2 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 65000' -c 'end' -c 'write'")
                run("docker exec r3 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 65000' -c 'end' -c 'write'")
                time.sleep(3)
                # Enable Southern path
                run("docker exec r1 vtysh -c 'configure terminal' -c 'interface eth2' -c 'ip ospf cost 5' -c 'end' -c 'write'")
                run("docker exec r4 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 5' -c 'end' -c 'write'")
                run("docker exec r4 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 5' -c 'end' -c 'write'")
                run("docker exec r3 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 5' -c 'end' -c 'write'")
                time.sleep(3)

        if path == "north":
                # Disable Southern path
                run("docker exec r1 vtysh -c 'configure terminal' -c 'interface eth2' -c 'ip ospf cost 65000' -c 'end' -c 'write'")
                run("docker exec r4 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 65000' -c 'end' -c 'write'")
                run("docker exec r4 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 65000' -c 'end' -c 'write'")
                run("docker exec r3 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 65000' -c 'end' -c 'write'")
                time.sleep(3)
                # Enable Northern path
                run("docker exec r1 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 5' -c 'end' -c 'write'")
                run("docker exec r2 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 5' -c 'end' -c 'write'")
                run("docker exec r2 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 5' -c 'end' -c 'write'")
                run("docker exec r3 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 5' -c 'end' -c 'write'")
                time.sleep(3)

def configure_hosts():
        print("Setting up host routes")
        # ha -> hb
        run("docker exec ha ip route replace default via 172.30.14.40")
        # hb -> ha
        run("docker exec hb ip route replace default via 172.30.35.10")

def compose_network():
        run("docker compose up -d --build")
        print("Starting containers")

def init_network():
        print("Initialize network")
        configure_hosts()
        # Run test pings from ha to r1 and hb to r3
        run("docker exec -it ha ping -c 2 172.30.14.40")
        run("docker exec -it hb ping -c 2 172.30.35.10")
        time.sleep(1)
        run("docker exec -it ha ping -c 2 172.30.35.30")
        set_costs("north")

def main():
        if len(sys.argv) < 2:
                print("Usage: python3 Logan_Hunter_u1342460.py <command>\n"
                        "Commands:\n"
                        " init                  Initialize network configuration\n"
                        " switch <north|south>  Change traffic path")
                return

        cmd = sys.argv[1].lower()

        if cmd == "-h":
                print("Usage: {sys.argv[0]} [options] <command>\n"
                " PA3 Network Orchestrator:\n"
                " Commands:\n"
                " compose               Compose the docker container network topology\n"
                " start                 Initialize OSPF and install host routes.\n"
                " switch north          Change traffic path to north HA <-> R1 <-> R2 <-> R3 <-> HB\n"
                " switch south          Change traffic path to south HA <-> R1 <-> R4 <-> R3 <-> HB\n"
                " options:\n"
                " -h                    Show this help menu")
                return

        if cmd == "compose":
                print("Composing network topology")
                compose_network()

        if cmd == "start":
                print("Installing host routes")
                init_network()

        elif cmd == "switch":
                if len(sys.argv) !=3:
                        print("Usage: python3 Logan_Hunter_u1342460.py switch 'north' or 'south'")
                        return
                direction = sys.argv[2].lower()
                if direction not in ("north", "south"):
                        print("Direction must be north or south")
                        return
                print(f"Changing path to {direction}")
                set_costs(direction)

        else:
                print("Invalid command")

if __name__ == "__main__":
        main()
